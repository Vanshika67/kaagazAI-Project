"""
Delete Pages — removes the specified page numbers from a PDF
and returns a new PDF with the remaining pages.
"""

from pathlib import Path
from typing import List

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def delete_pages(input_path: Path, pages_to_delete: List[int]) -> Path:
    """pages_to_delete: list of 1-indexed page numbers to remove."""
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)

    invalid = [p for p in pages_to_delete if p < 1 or p > total_pages]
    if invalid:
        raise ValueError(f"Invalid page number(s): {invalid}. PDF has {total_pages} pages.")

    delete_set = set(pages_to_delete)
    writer = PdfWriter()

    for i in range(total_pages):
        page_number = i + 1
        if page_number not in delete_set:
            writer.add_page(reader.pages[i])

    if len(writer.pages) == 0:
        raise ValueError("Cannot delete all pages — the resulting PDF would be empty.")

    output_path = make_output_path("deleted_pages")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path