"""
Remove Blank Pages — automatically detects and removes pages that have
no meaningful content (no text, no images), using PyMuPDF (fitz) to
inspect each page's actual content.
"""

from pathlib import Path
from typing import Tuple

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def _is_page_blank(page: "fitz.Page", text_threshold: int = 5) -> bool:
    """
    A page is considered blank if:
    - it has little to no extractable text (below text_threshold characters), AND
    - it has no embedded images.
    """
    text = page.get_text().strip()
    has_meaningful_text = len(text) > text_threshold

    images = page.get_images(full=True)
    has_images = len(images) > 0

    return not has_meaningful_text and not has_images


def remove_blank_pages(input_path: Path) -> Tuple[Path, list]:
    """
    Returns (output_path, removed_page_numbers).
    removed_page_numbers are 1-indexed, based on the ORIGINAL document,
    so the caller can tell the user exactly which pages were dropped.
    """
    doc = fitz.open(str(input_path))
    total_pages = doc.page_count

    blank_pages = set()
    for i in range(total_pages):
        page = doc.load_page(i)
        if _is_page_blank(page):
            blank_pages.add(i + 1)  # store as 1-indexed
    doc.close()

    if len(blank_pages) == total_pages:
        raise ValueError("Every page appears blank — cannot produce an empty PDF.")

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for i in range(total_pages):
        page_number = i + 1
        if page_number not in blank_pages:
            writer.add_page(reader.pages[i])

    output_path = make_output_path("no_blanks")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path, sorted(blank_pages)