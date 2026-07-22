"""Configuration dataclass for processing settings."""

from dataclasses import dataclass, field


@dataclass
class ProcessingSettings:
    """Settings for batch image processing.

    Attributes:
        remove_bg: Whether to remove background using rembg.
        trim_edges: Whether to trim transparent edges.
        uniform_size: Whether to resize all images to the same dimensions.
        target_width: Target width in pixels for uniform resizing.
        target_height: Target height in pixels for uniform resizing.
        center_object: Whether to center the object on the canvas.
        overwrite_existing: Whether to overwrite existing output files.
        preserve_structure: Whether to preserve input folder structure.
    """

    remove_bg: bool = True
    trim_edges: bool = True
    uniform_size: bool = False
    target_width: int = 512
    target_height: int = 512
    center_object: bool = False
    overwrite_existing: bool = False
    preserve_structure: bool = True


@dataclass
class ProcessingResult:
    """Result of processing a single image.

    Attributes:
        input_path: Path to the input image.
        output_path: Path to the output image, or None on failure.
        success: Whether processing was successful.
        error: Error message if processing failed.
        elapsed_ms: Processing time in milliseconds.
    """

    input_path: str
    output_path: str | None = None
    success: bool = False
    error: str | None = None
    elapsed_ms: float = 0.0
