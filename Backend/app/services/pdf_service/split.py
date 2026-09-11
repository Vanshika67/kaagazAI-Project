"""
Split PDF — breaks one PDF into multiple single/range PDFs
and returns them all zipped together.
"""

import zipfile
from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def split_pdf(input_path: Path, ranges: List[Tuple[int, int]] = None) -> Path:
    """
    ranges: list of (start_page, end_page) tuples, 1-indexed, inclusive.
    If ranges is None, splits into one PDF per page.
    Returns the path to a ZIP file containing all resulting PDFs.
    """
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)

    if not ranges:
        ranges = [(i + 1, i + 1) for i in range(total_pages)]

    output_files = []
    for idx, (start, end) in enumerate(ranges, start=1):
        if start < 1 or end > total_pages or start > end:
            raise ValueError(f"Invalid page range: {start}-{end} (PDF has {total_pages} pages)")

        writer = PdfWriter()
        for page_num in range(start - 1, end):
            writer.add_page(reader.pages[page_num])

        part_path = make_output_path(f"split_part{idx}")
        with open(part_path, "wb") as f:
            writer.write(f)
        output_files.append(part_path)

    zip_path = make_output_path("split_result", suffix=".zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file_path in output_files:
            zipf.write(file_path, arcname=file_path.name)
            file_path.unlink()

    return zip_path