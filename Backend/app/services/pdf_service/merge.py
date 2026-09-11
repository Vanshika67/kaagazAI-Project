"""
Merge PDF — combines multiple PDF files into a single PDF,
in the order the files are provided.
"""

from pathlib import Path
from typing import List

from pypdf import PdfWriter

from app.utils.file_handler import make_output_path


def merge_pdfs(input_paths: List[Path]) -> Path:
    writer = PdfWriter()

    for path in input_paths:
        writer.append(str(path))

    output_path = make_output_path("merged")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path