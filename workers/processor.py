"""Background worker thread for batch image processing."""

from __future__ import annotations

import os
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Event

import PIL.Image
from PySide6.QtCore import QThread, Signal

from utils.config import ProcessingResult, ProcessingSettings
from utils.file_utils import build_output_path, ensure_output_dir, find_images
from image_processing.bg_remover import remove_background
from image_processing.trimmer import trim_transparent
from image_processing.resizer import resize_to_fit


class ProcessingWorker(QThread):
    """Worker thread that processes images in parallel using a thread pool.

    Emits signals to update the UI without blocking the main thread.

    Signals:
        log_message: Emitted for each processing event (filename, status, level).
        progress_updated: Emitted periodically (processed, total, elapsed_s, eta_s).
        scan_complete: Emitted when folder scan is done (total_images).
        processing_finished: Emitted when all processing is complete (success_count, fail_count).
        stopped: Emitted when processing is cancelled by user.
    """

    log_message = Signal(str, str, str)  # filename, status, level (info/success/error)
    progress_updated = Signal(int, int, float, float)  # processed, total, elapsed_s, eta_s
    scan_complete = Signal(int)  # total_images
    processing_finished = Signal(int, int)  # success_count, fail_count
    stopped = Signal()

    def __init__(self, parent=None):
        """Initialize the worker thread."""
        super().__init__(parent)
        self._images: tuple[Path, ...] = ()
        self._input_root = Path()
        self._output_root = Path()
        self._settings = ProcessingSettings()
        self._stop_event = Event()
        self._start_time = 0.0
        self._processed = 0
        self._success = 0
        self._fail = 0
        self._lock = __import__('threading').Lock()

    def configure(
        self,
        input_folder: str,
        output_folder: str,
        settings: ProcessingSettings,
    ) -> None:
        """Configure the worker with processing parameters.

        Args:
            input_folder: Path to the input folder containing images.
            output_folder: Path to the output folder for processed images.
            settings: Processing settings dataclass.
        """
        self._input_root = Path(input_folder).resolve()
        self._output_root = Path(output_folder).resolve()
        self._settings = settings

    def stop(self) -> None:
        """Signal the worker to stop processing.

        Sets the stop event flag. The worker will finish the current
        image being processed and then exit.
        """
        self._stop_event.set()

    def run(self) -> None:
        """Main processing loop. Runs in a background thread.

        Scans the input folder for images, then processes them in parallel
        using ThreadPoolExecutor with a number of workers equal to the
        CPU core count.
        """
        self._stop_event.clear()
        self._processed = 0
        self._success = 0
        self._fail = 0

        if not self._input_root.exists():
            self.log_message.emit('', f'Input folder does not exist: {self._input_root}', 'error')
            self.processing_finished.emit(0, 0)
            return

        self.log_message.emit('', f'Scanning folder: {self._input_root}', 'info')
        self._images = find_images(self._input_root)

        total = len(self._images)
        self.scan_complete.emit(total)
        self.log_message.emit('', f'Found {total} image(s) to process', 'info')

        if total == 0:
            self.processing_finished.emit(0, 0)
            return

        max_workers = os.cpu_count() or 4
        self.log_message.emit('', f'Using {max_workers} worker threads', 'info')

        self._start_time = time.perf_counter()
        futures: dict[Future, Path] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for img_path in self._images:
                future = executor.submit(self._process_single, img_path)
                futures[future] = img_path

            for future in as_completed(futures):
                if self._stop_event.is_set():
                    self.log_message.emit('', 'Processing stopped by user', 'info')
                    break

                img_path = futures[future]
                try:
                    result: ProcessingResult = future.result(timeout=30)
                except Exception as e:
                    result = ProcessingResult(
                        input_path=str(img_path),
                        success=False,
                        error=str(e),
                    )

                with self._lock:
                    self._processed += 1
                    if result.success:
                        self._success += 1
                    else:
                        self._fail += 1

                self._emit_result(result)
                self._emit_progress(total)

        if self._stop_event.is_set():
            self.stopped.emit()
            self.log_message.emit(
                '',
                f'Done: {self._success} succeeded, {self._fail} failed (stopped early)',
                'info',
            )
        else:
            self.log_message.emit(
                '',
                f'Done: {self._success} succeeded, {self._fail} failed',
                'info',
            )

        self.processing_finished.emit(self._success, self._fail)

    def _process_single(self, img_path: Path) -> ProcessingResult:
        """Process a single image.

        Args:
            img_path: Path to the input image file.

        Returns:
            ProcessingResult with success/error status.
        """
        t_start = time.perf_counter()

        try:
            if self._stop_event.is_set():
                return ProcessingResult(
                    input_path=str(img_path),
                    success=False,
                    error='Cancelled',
                )

            image = PIL.Image.open(img_path)

            if self._settings.remove_bg:
                image = remove_background(image)

            if self._settings.trim_edges:
                image = trim_transparent(image)

            if self._settings.uniform_size:
                image = resize_to_fit(
                    image,
                    self._settings.target_width,
                    self._settings.target_height,
                    center=self._settings.center_object,
                )

            output_path = build_output_path(
                img_path,
                self._input_root,
                self._output_root,
                preserve_structure=self._settings.preserve_structure,
            )

            if not self._settings.overwrite_existing and output_path.exists():
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

    def _emit_result(self, result: ProcessingResult) -> None:
        """Emit a log message for a processing result.

        Args:
            result: The processing result to log.
        """
        fname = Path(result.input_path).name
        if result.success:
            elapsed = result.elapsed_ms / 1000
            self.log_message.emit(
                fname,
                f'OK ({elapsed:.1f}s) -> {Path(result.output_path).name}',
                'success',
            )
        else:
            self.log_message.emit(fname, f'FAILED: {result.error}', 'error')

    def _emit_progress(self, total: int) -> None:
        """Emit progress update signal.

        Args:
            total: Total number of images to process.
        """
        elapsed_s = time.perf_counter() - self._start_time
        if self._processed > 0 and self._processed < total:
            eta_s = (elapsed_s / self._processed) * (total - self._processed)
        else:
            eta_s = 0.0
        self.progress_updated.emit(self._processed, total, elapsed_s, eta_s)
