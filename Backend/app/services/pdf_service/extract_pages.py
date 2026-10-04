"""
Extract Pages — creates a new PDF containing only the specified pages,
in the exact order given (useful for pulling out a subset like "3,1,5").
"""

from pathlib import Path
from typing import List

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def extract_pages(input_path: Path, pages: List[int]) -> Path:
    """pages: 1-indexed page numbers, in the order they should appear in the output."""
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)

    invalid = [p for p in pages if p < 1 or p > total_pages]
    if invalid:
        raise ValueError(f"Invalid page number(s): {invalid}. PDF has {total_pages} pages.")

    if not pages:
        raise ValueError("At least one page number must be provided.")

    writer = PdfWriter()
    for page_number in pages:
        writer.add_page(reader.pages[page_number - 1])

    output_path = make_output_path("extracted")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path