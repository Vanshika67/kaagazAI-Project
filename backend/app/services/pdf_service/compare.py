"""
Compare PDF — extracts text from two PDFs page-by-page and produces
a human-readable diff report highlighting additions and deletions.
"""

import difflib
from pathlib import Path

import fitz  # PyMuPDF


def compare_pdfs(path_a: Path, path_b: Path) -> str:
    doc_a = fitz.open(str(path_a))
    doc_b = fitz.open(str(path_b))

    text_a = []
    for page in doc_a:
        text_a.extend(page.get_text().splitlines())

    text_b = []
    for page in doc_b:
        text_b.extend(page.get_text().splitlines())

    doc_a.close()
    doc_b.close()

    diff = difflib.unified_diff(
        text_a, text_b,
        fromfile="Document A", tofile="Document B",
        lineterm="",
    )

    report_lines = list(diff)
    if not report_lines:
        return "No differences found — the two PDFs contain identical text."

    return "\n".join(report_lines)