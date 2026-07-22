"""Image processing functions for the HTTP API.

Reuses the existing image_processing and utils modules.
Does NOT duplicate business logic from workers/processor.py.
"""

from __future__ import annotations

import io
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Event
from typing import Callable

import PIL.Image

from image_processing.bg_remover import remove_background
from image_processing.trimmer import trim_transparent
from image_processing.resizer import resize_to_fit
from utils.config import ProcessingResult, ProcessingSettings
from utils.file_utils import build_output_path, ensure_output_dir, find_images


def process_single_image(
    img_path: Path,
    input_root: Path,
    output_root: Path,
    settings: ProcessingSettings,
    stop_event: Event | None = None,
) -> ProcessingResult:
    """Process a single image: remove background, trim, resize.

    Uses the same image_processing functions as the GUI worker,
    ensuring consistent results.

    Args:
        img_path: Path to the input image file.
        input_root: Root folder of the input structure.
        output_root: Root folder for output.
        settings: Processing settings dataclass.
        stop_event: Optional event for cancellation.

    Returns:
        ProcessingResult with success/error status.
    """
    t_start = time.perf_counter()

    try:
        if stop_event and stop_event.is_set():
            return ProcessingResult(
                input_path=str(img_path),
                success=False,
                error='Cancelled',
            )

        image = PIL.Image.open(img_path)

        if settings.remove_bg:
            image = remove_background(image)

        if settings.trim_edges:
            image = trim_transparent(image)

        if settings.uniform_size:
            image = resize_to_fit(
                image,
                settings.target_width,
                settings.target_height,
                center=settings.center_object,
            )

        output_path = build_output_path(
            img_path, input_root, output_root,
            preserve_structure=settings.preserve_structure,
        )

        if not settings.overwrite_existing and output_path.exists():
            return ProcessingResult(
                input_path=str(img_path),
                output_path=str(output_path),
                success=False,
                error='Output file already exists (skipping)',
                elapsed_ms=(time.perf_counter() - t_start) * 1000,
            )

        ensure_output_dir(output_path)
        image.save(output_path, 'PNG', optimize=True)

        return ProcessingResult(
            input_path=str(img_path),
            output_path=str(output_path),
            success=True,
            elapsed_ms=(time.perf_counter() - t_start) * 1000,
        )

    except Exception as e:
        return ProcessingResult(
            input_path=str(img_path),
            success=False,
            error=str(e),
            elapsed_ms=(time.perf_counter() - t_start) * 1000,
        )


def process_folder_task(
    input_folder: str,
    output_folder: str,
    settings: ProcessingSettings,
    stop_event: Event,
    progress_callback: Callable[[int, int, float, float, ProcessingResult], None] | None = None,
) -> tuple[int, int, int]:
    """Process all images in a folder using ThreadPoolExecutor.

    Args:
        input_folder: Path to the input folder.
        output_folder: Path to the output folder.
        settings: Processing settings dataclass.
        stop_event: Event to signal cancellation.
        progress_callback: Called after each image: (processed, total, elapsed_s, eta_s, result).

    Returns:
        Tuple of (total_images, success_count, fail_count).
    """
    input_root = Path(input_folder).resolve()
    output_root = Path(output_folder).resolve()
    
    if not input_root.exists():
        return (0, 0, 0)

    images = find_images(input_root)
    total = len(images)

    if total == 0:
        return (0, 0, 0)

    max_workers = os.cpu_count() or 4
    processed = 0
    success = 0
    fail = 0
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_single_image, img, input_root, output_root, settings, stop_event,
            ): img
            for img in images
        }

        for future in as_completed(futures):
            if stop_event.is_set():
                break

            img_path = futures[future]
            try:
                result = future.result(timeout=30)
            except Exception as e:
                result = ProcessingResult(
                    input_path=str(img_path),
                    success=False,
                    error=str(e),
                )

            processed += 1
            if result.success:
                success += 1
            else:
                fail += 1

            elapsed_s = time.perf_counter() - start_time
            if processed < total:
                eta_s = (elapsed_s / processed) * (total - processed)
            else:
                eta_s = 0.0

            if progress_callback:
                progress_callback(processed, total, elapsed_s, eta_s, result)

    return (total, success, fail)


def process_single_file_to_bytes(
    file_data: bytes | None = None,
    file_path: str | None = None,
    settings: ProcessingSettings | None = None,
) -> bytes | None:
    """Process a single image file and return PNG bytes.

    Args:
        file_data: Raw image bytes (from multipart upload).
        file_path: Path to the image file on disk.
        settings: Processing settings. Defaults to full processing.

    Returns:
        PNG bytes of the processed image, or None on failure.
    """
    if settings is None:
        settings = ProcessingSettings()

    try:
        if file_data is not None:
            image = PIL.Image.open(io.BytesIO(file_data))
        elif file_path is not None:
            image = PIL.Image.open(file_path)
        else:
            return None

        if settings.remove_bg:
            image = remove_background(image)

        if settings.trim_edges:
            image = trim_transparent(image)

        if settings.uniform_size:
            image = resize_to_fit(
                image,
                settings.target_width,
                settings.target_height,
                center=settings.center_object,
            )

        buf = io.BytesIO()
        image.save(buf, 'PNG', optimize=True)
        buf.seek(0)
        return buf.getvalue()

    except Exception:
        return None
