"""
Crop PDF — trims the visible area of every page by shrinking its
mediabox (the page's visible boundary), effectively cutting off
margins on each side.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def crop_pdf(
    input_path: Path,
    left: float = 0,
    bottom: float = 0,
    right: float = 0,
    top: float = 0,
) -> Path:
    """
    left/bottom/right/top: how many points (1/72 inch) to trim off each side.
    e.g. left=20 trims 20 points off the left edge of every page.
    """
    if any(v < 0 for v in (left, bottom, right, top)):
        raise ValueError("Crop values cannot be negative.")

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        box = page.mediabox
        new_left = float(box.left) + left
        new_bottom = float(box.bottom) + bottom
        new_right = float(box.right) - right
        new_top = float(box.top) - top

        if new_left >= new_right or new_bottom >= new_top:
            raise ValueError("Crop values are too large — the page would have no visible area left.")

        page.mediabox.left = new_left
        page.mediabox.bottom = new_bottom
        page.mediabox.right = new_right
        page.mediabox.top = new_top

        writer.add_page(page)

    output_path = make_output_path("cropped")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path