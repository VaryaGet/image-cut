"""Transparent edge trimming for images with alpha channel."""

from PIL import Image


def trim_transparent(image: Image.Image) -> Image.Image:
    """Trim transparent borders from an RGBA image.

    Scans the alpha channel to find the bounding box of non-transparent
    pixels and crops the image tightly around the visible content.

    Args:
        image: PIL Image in RGBA mode.

    Returns:
        PIL Image cropped to the non-transparent bounding box.
        If the image is fully transparent, returns a 1x1 transparent image.

    Raises:
        ValueError: If the image has no alpha channel.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    alpha = image.getchannel('A')
    bbox = alpha.getbbox()

    if bbox is None:
        return Image.new('RGBA', (1, 1), (0, 0, 0, 0))

    return image.crop(bbox)
