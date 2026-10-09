"""
HTML <-> PDF conversions.
"""

from pathlib import Path

from weasyprint import HTML
import fitz  # PyMuPDF

from app.utils.file_handler import make_output_path


def html_to_pdf(html_content: str) -> Path:
    output_path = make_output_path("html_to_pdf")
    HTML(string=html_content).write_pdf(str(output_path))
    return output_path


def pdf_to_html(input_path: Path) -> Path:
    doc = fitz.open(str(input_path))

    html_parts = ["<html><body>"]
    for i, page in enumerate(doc, start=1):
        html_parts.append(f"<h2>Page {i}</h2>")
        html_parts.append(page.get_text("html"))
    html_parts.append("</body></html>")
    doc.close()

    output_path = make_output_path("pdf_to_html", suffix=".html")
    output_path.write_text("\n".join(html_parts), encoding="utf-8")

    return output_path