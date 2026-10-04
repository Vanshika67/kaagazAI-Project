"""
Sign PDF — stamps a signature image onto a chosen page at a chosen
position (a common, practical approach to "e-signing" a document).
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.utils.file_handler import make_output_path

POSITIONS = {"bottom-right", "bottom-left", "bottom-center"}


def sign_pdf(
    pdf_path: Path,
    signature_image_path: Path,
    page_number: int = -1,  # -1 means "last page"
    position: str = "bottom-right",
    width: float = 150,
    height: float = 60,
) -> Path:
    if position not in POSITIONS:
        raise ValueError(f"Invalid position '{position}'. Choose from {POSITIONS}.")

    doc = fitz.open(str(pdf_path))
    total_pages = doc.page_count

    target_index = total_pages - 1 if page_number == -1 else page_number - 1
    if target_index < 0 or target_index >= total_pages:
        raise ValueError(f"Invalid page number. PDF has {total_pages} pages.")

    page = doc.load_page(target_index)
    page_width, page_height = page.rect.width, page.rect.height
    margin = 30

    if position == "bottom-right":
        rect = fitz.Rect(page_width - width - margin, page_height - height - margin,
                          page_width - margin, page_height - margin)
    elif position == "bottom-left":
        rect = fitz.Rect(margin, page_height - height - margin,
                          margin + width, page_height - margin)
    else:
        x_center = page_width / 2
        rect = fitz.Rect(x_center - width / 2, page_height - height - margin,
                          x_center + width / 2, page_height - margin)

    page.insert_image(rect, filename=str(signature_image_path))

    output_path = make_output_path("signed")
    doc.save(str(output_path))
    doc.close()

    return output_path