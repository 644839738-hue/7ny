"""
Low-level image processing helpers built on Pillow.

All functions operate on ``PIL.Image.Image`` objects and are stateless.
"""

from __future__ import annotations

from typing import Optional

from PIL import Image


def has_alpha(image: Image.Image) -> bool:
    """Return True if *image* has an alpha (transparency) channel."""
    return image.mode in ("RGBA", "LA", "PA") or (
        image.mode == "P" and "transparency" in image.info
    )


def get_content_bbox(image: Image.Image) -> Optional[tuple[int, int, int, int]]:
    """Return the bounding box ``(left, top, right, bottom)`` of
    non‑transparent pixels, or ``None`` if the image is fully transparent.

    If *image* has no alpha channel the full image bounds are returned.
    """
    if not has_alpha(image):
        return (0, 0, image.width, image.height)

    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    return bbox


def trim_transparent_edges(image: Image.Image) -> Image.Image:
    """Crop transparent edges from *image*.

    * If the image has an alpha channel, crop to the bounding box of
      non‑transparent pixels.
    * If the image has no alpha channel, return it unchanged.
    """
    bbox = get_content_bbox(image)
    if bbox is None:
        # Fully transparent — return a 1×1 transparent pixel
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    if bbox == (0, 0, image.width, image.height):
        return image.copy()

    return image.crop(bbox)


def remove_background(image: Image.Image) -> Image.Image:
    """Placeholder for AI‑powered background removal (e.g. rembg).

    Currently a no‑op — returns *image* unchanged.  To enable real
    background removal, install ``rembg`` and replace this body with::

        from rembg import remove
        return remove(image)

    Args:
        image: Input PIL image (any mode).

    Returns:
        The image with background removed (RGBA), or the input unchanged
        if already RGBA, or the stub placeholder.
    """
    # ----------------------------------------------------------------
    # Stub — replace with rembg or similar when available
    # ----------------------------------------------------------------
    if image.mode != "RGBA":
        return image.convert("RGBA")
    return image.copy()


def resize_to_target(
    image: Image.Image,
    target_size: int,
    allow_upscale: bool = False,
) -> Image.Image:
    """Resize *image* so its larger dimension equals *target_size* pixels,
    preserving aspect ratio.  The image is then pasted onto a square canvas
    and centred.

    Args:
        image: Input image.
        target_size: Desired square side length in pixels.
        allow_upscale: If ``False``, do not enlarge images smaller than
            *target_size* (they stay at their original size, centred).

    Returns:
        A new ``RGBA`` image of size ``(target_size, target_size)``.
    """
    w, h = image.size
    scale = target_size / max(w, h) if max(w, h) > 0 else 1.0

    if not allow_upscale and scale > 1.0:
        scale = 1.0

    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    resized = image.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized if resized.mode == "RGBA" else None)

    return canvas


def process_asset(
    image: Image.Image,
    target_size: int,
    *,
    trim: bool = True,
    centre: bool = True,
    allow_upscale: bool = False,
) -> tuple[Image.Image, dict]:
    """Run the full post‑processing pipeline on a single asset image.

    Pipeline order:
        1. (future) remove_background
        2. trim_transparent_edges
        3. resize_to_target + centre

    Returns ``(processed_image, info_dict)``.
    """
    info: dict = {
        "original_size": list(image.size),
    }

    if trim:
        image = trim_transparent_edges(image)

    info["trimmed_size"] = list(image.size)

    if centre:
        image = resize_to_target(image, target_size, allow_upscale=allow_upscale)

    info["final_size"] = list(image.size)
    return image, info
