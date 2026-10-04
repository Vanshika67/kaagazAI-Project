"""
Reorder Pages — rearranges ALL pages of a PDF into a new order
(different from Extract Pages, which can also drop pages —
here every original page must appear exactly once).
"""

from pathlib import Path
from typing import List

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def reorder_pages(input_path: Path, new_order: List[int]) -> Path:
    """new_order: 1-indexed page numbers, e.g. [3,1,2] for a 3-page PDF."""
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)

    if sorted(new_order) != list(range(1, total_pages + 1)):
        raise ValueError(
            f"new_order must contain every page number from 1 to {total_pages} exactly once. "
            f"Got: {new_order}"
        )

    writer = PdfWriter()
    for page_number in new_order:
        writer.add_page(reader.pages[page_number - 1])

    output_path = make_output_path("reordered")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path