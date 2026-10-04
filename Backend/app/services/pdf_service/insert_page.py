"""
Insert Page — inserts the pages of one PDF into another PDF
at a specific position (not just at the start or end).

Core idea: split the original PDF into "before" and "after" halves
around the insert position, then stitch: before + new_pages + after.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def insert_page(original_path: Path, new_pages_path: Path, after_page: int) -> Path:
    """
    after_page: the new content is inserted immediately AFTER this page number
    (1-indexed). Use after_page=0 to insert at the very beginning.
    """
    original_reader = PdfReader(str(original_path))
    new_reader = PdfReader(str(new_pages_path))
    total_pages = len(original_reader.pages)

    if after_page < 0 or after_page > total_pages:
        raise ValueError(
            f"Invalid position: {after_page}. Original PDF has {total_pages} pages "
            f"(valid range is 0 to {total_pages})."
        )

    writer = PdfWriter()

    # 1. Pages before the insertion point
    for i in range(0, after_page):
        writer.add_page(original_reader.pages[i])

    # 2. The new pages being inserted
    for page in new_reader.pages:
        writer.add_page(page)

    # 3. Remaining original pages after the insertion point
    for i in range(after_page, total_pages):
        writer.add_page(original_reader.pages[i])

    output_path = make_output_path("inserted")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path