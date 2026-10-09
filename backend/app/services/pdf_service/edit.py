"""
Edit PDF — adds a new text annotation at a given (x, y) position on a
chosen page.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.utils.file_handler import make_output_path


def add_text_to_pdf(
    input_path: Path,
    page_number: int,
    text: str,
    x: float,
    y: float,
    font_size: float = 12,
    color: tuple = (0, 0, 0),
) -> Path:
    doc = fitz.open(str(input_path))
    total_pages = doc.page_count

    if page_number < 1 or page_number > total_pages:
        raise ValueError(f"Invalid page number. PDF has {total_pages} pages.")

    page = doc.load_page(page_number - 1)
    page.insert_text((x, y), text, fontsize=font_size, color=color)

    output_path = make_output_path("edited")
    doc.save(str(output_path))
    doc.close()

    return output_path