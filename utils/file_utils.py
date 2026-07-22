"""File system utilities for image discovery and output management."""

from pathlib import Path

SUPPORTED_EXTENSIONS: tuple[str, ...] = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')


def find_images(folder: Path) -> tuple[Path, ...]:
    """Recursively find all supported image files in a folder.

    Args:
        folder: Root folder to search.

    Returns:
        Sorted tuple of Path objects pointing to image files.
    """
    images: list[Path] = []
    for ext in SUPPORTED_EXTENSIONS:
        images.extend(folder.rglob(f'*{ext}'))
    return tuple(sorted(images))


def build_output_path(
    input_file: Path,
    input_root: Path,
    output_root: Path,
    preserve_structure: bool = True,
) -> Path:
    """Build the output path for a processed image.

    Args:
        input_file: Path to the input image file.
        input_root: Root folder of the input structure.
        output_root: Root folder for output.
        preserve_structure: If True, mirror the folder structure.

    Returns:
        Path object pointing to the output .png file.
    """
    if preserve_structure:
        relative = input_file.relative_to(input_root)
        out_path = output_root / relative.with_suffix('.png')
    else:
        out_path = output_root / f'{input_file.stem}.png'

    return out_path.resolve()


def ensure_output_dir(file_path: Path) -> None:
    """Create parent directories for an output file if they don't exist.

    Args:
        file_path: Path to the output file whose parent should exist.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


def count_images_by_folder(images: tuple[Path, ...]) -> int:
    """Count the number of images in a tuple.

    Args:
        images: Tuple of image paths.

    Returns:
        Number of images.
    """
    return len(images)
