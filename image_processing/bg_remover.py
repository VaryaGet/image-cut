"""Background removal using rembg with ONNX runtime backend."""

from io import BytesIO

import numpy as np
from PIL import Image


def remove_background(image: Image.Image) -> Image.Image:
    """Remove background from an image using rembg.

    Converts the image to RGBA with transparent background.
    The function uses rembg's `remove` with ONNX runtime backend,
    operating entirely locally with no network calls.

    Args:
        image: PIL Image in any mode.

    Returns:
        PIL Image in RGBA mode with background removed.

    Raises:
        ImportError: If rembg is not installed.
        Exception: If background removal fails for any reason.
    """
    from rembg import remove

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)

    result_data = remove(buf.getvalue())

    result = Image.open(BytesIO(result_data)).convert('RGBA')
    return result


def ensure_rgba(image: Image.Image) -> Image.Image:
    """Convert an image to RGBA mode if needed.

    Args:
        image: PIL Image in any mode.

    Returns:
        PIL Image in RGBA mode.
    """
    if image.mode != 'RGBA':
        return image.convert('RGBA')
    return image
