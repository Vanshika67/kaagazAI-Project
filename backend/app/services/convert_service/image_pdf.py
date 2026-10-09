"""
Image to PDF — converts one or more images (JPG/PNG) into a single PDF,
one image per page, in the order given.
"""

from pathlib import Path
from typing import List

from PIL import Image

from app.utils.file_handler import make_output_path


def images_to_pdf(image_paths: List[Path]) -> Path:
    if not image_paths:
        raise ValueError("At least one image is required.")

    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        images.append(img)

    output_path = make_output_path("images_to_pdf")

    first_image, remaining_images = images[0], images[1:]
    first_image.save(output_path, save_all=True, append_images=remaining_images)

    return output_path