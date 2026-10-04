"""
Rotate PDF — rotates all pages, or only specific pages, by a given angle.
"""

from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def rotate_pdf(input_path: Path, angle: int, pages: Optional[List[int]] = None) -> Path:
    """
    angle: rotation in degrees, must be a multiple of 90 (90, 180, 270, -90 etc.)
    pages: 1-indexed page numbers to rotate. If None, rotates every page.
    """
    if angle % 90 != 0:
        raise ValueError("Angle must be a multiple of 90 (e.g. 90, 180, 270).")

    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)
    writer = PdfWriter()

    target_pages = set(pages) if pages else set(range(1, total_pages + 1))

    invalid = [p for p in target_pages if p < 1 or p > total_pages]
    if invalid:
        raise ValueError(f"Invalid page number(s): {invalid}. PDF has {total_pages} pages.")

    for i in range(total_pages):
        page = reader.pages[i]
        if (i + 1) in target_pages:
            page.rotate(angle)
        writer.add_page(page)

    output_path = make_output_path("rotated")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path