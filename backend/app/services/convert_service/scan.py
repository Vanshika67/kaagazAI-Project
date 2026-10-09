"""
Scan PDF — takes photos of a document and enhances them to look like
a clean scan: grayscale, increased contrast, and sharpened, then
combines them into one PDF.
"""

from pathlib import Path
from typing import List

from PIL import Image, ImageOps, ImageEnhance

from app.utils.file_handler import make_output_path


def _enhance_scan(img: Image.Image) -> Image.Image:
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    return img.convert("RGB")


def scan_to_pdf(image_paths: List[Path]) -> Path:
    if not image_paths:
        raise ValueError("At least one image is required.")

    images = [_enhance_scan(Image.open(p)) for p in image_paths]

    output_path = make_output_path("scanned")
    first_image, remaining = images[0], images[1:]
    first_image.save(output_path, save_all=True, append_images=remaining)

    return output_path