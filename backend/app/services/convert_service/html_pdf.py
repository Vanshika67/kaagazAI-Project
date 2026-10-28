"""
html_pdf.py
------------
HTML <-> PDF conversion.

Uses xhtml2pdf (pure Python, no system dependencies) instead of
WeasyPrint, since WeasyPrint needs GTK libraries that are painful to
install on Windows.
"""

import os
import uuid
from typing import Optional

import pymupdf  # PyMuPDF
from xhtml2pdf import pisa

TEMP_DIR = os.path.abspath("app/temp_files")


def html_to_pdf(html_path_or_content, is_file: Optional[bool] = None) -> str:
    """
    Converts HTML (file path or raw HTML string) into a PDF.

    is_file:
        True  -> treat the argument as a path to an .html file
        False -> treat the argument as raw HTML text
        None  -> auto-detect (text containing '<' is treated as HTML content)
    """
    os.makedirs(TEMP_DIR, exist_ok=True)

    text = str(html_path_or_content)

    if is_file is None:
        is_file = ("<" not in text) and os.path.isfile(text)

    if is_file:
        with open(text, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        html_content = text

    if not html_content.strip():
        raise ValueError("HTML content is empty.")

    out_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.pdf")

    with open(out_path, "wb") as out_file:
        result = pisa.CreatePDF(html_content, dest=out_file)

    if result.err:
        raise RuntimeError("Failed to convert HTML to PDF.")

    return out_path


def pdf_to_html(pdf_path) -> str:
    """
    Converts each page of a PDF into HTML and combines them into
    one HTML file.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    out_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.html")

    doc = pymupdf.open(str(pdf_path))
    try:
        html_parts = ["<html><body>"]
        for page in doc:
            html_parts.append(page.get_text("html"))
        html_parts.append("</body></html>")
    finally:
        doc.close()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    return out_path