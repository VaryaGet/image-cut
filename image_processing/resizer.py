"""Resize images to uniform dimensions with aspect ratio preservation."""

from PIL import Image


def resize_to_fit(
    image: Image.Image,
    target_width: int,
    target_height: int,
    center: bool = True,
) -> Image.Image:
    """Resize image to fit within target dimensions, preserving aspect ratio.

    The image is scaled to fit entirely within the target canvas while
    maintaining its proportions. Transparent padding is added to fill
    the remaining space.

    Args:
        image: PIL Image in RGBA mode.
        target_width: Desired canvas width in pixels.
        target_height: Desired canvas height in pixels.
        center: If True, center the image on the canvas.
                If False, place at top-left corner.

    Returns:
        PIL Image with dimensions (target_width, target_height)
        in RGBA mode.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    if image.width == 0 or image.height == 0:
        return Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))

    scale_x = target_width / image.width
    scale_y = target_height / image.height
    scale = min(scale_x, scale_y, 1.0)

    new_width = max(1, int(image.width * scale))
    new_height = max(1, int(image.height * scale))

    if scale < 1.0:
        resized = image.resize((new_width, new_height), Image.LANCZOS)
    else:
        resized = image

    canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))

    if center:
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2
    else:
        offset_x = 0
        offset_y = 0

    canvas.paste(resized, (offset_x, offset_y), resized)
    return canvas
