"""
Page Manager — the most flexible page-organizing tool: it treats a PDF's
pages as separate, independent units that can be freely rearranged,
removed, or mixed with pages from OTHER uploaded PDFs, all in one go.

Instead of separate "insert", "delete", "reorder" tools, the caller
just describes the FINAL page order they want as a "plan":

    plan = [
        {"source": "main", "page": 1},      # keep page 1 of the main file
        {"source": "extra_0", "page": 1},   # insert page 1 of the 1st extra file here
        {"source": "main", "page": 3},      # then page 3 of the main file
        # page 2 of main is simply left out -> effectively "deleted"
    ]
"""

from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def manage_pages(main_path: Path, extra_paths: List[Path], plan: List[Dict]) -> Path:
    if not plan:
        raise ValueError("Plan cannot be empty — describe at least one page for the output.")

    readers = {"main": PdfReader(str(main_path))}
    for i, path in enumerate(extra_paths):
        readers[f"extra_{i}"] = PdfReader(str(path))

    writer = PdfWriter()

    for i, step in enumerate(plan):
        source = step.get("source")
        page_number = step.get("page")

        if source not in readers:
            raise ValueError(
                f"Plan item {i + 1}: unknown source '{source}'. "
                f"Available: {list(readers.keys())}"
            )

        reader = readers[source]
        total_pages = len(reader.pages)

        if not isinstance(page_number, int) or page_number < 1 or page_number > total_pages:
            raise ValueError(
                f"Plan item {i + 1}: invalid page {page_number} for source '{source}' "
                f"(it has {total_pages} pages)."
            )

        writer.add_page(reader.pages[page_number - 1])

    output_path = make_output_path("managed_pages")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def get_page_count(pdf_path: Path) -> int:
    """Helper so the frontend can know how many pages a file has before building a plan."""
    return len(PdfReader(str(pdf_path)).pages)