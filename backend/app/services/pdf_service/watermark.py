"""
Watermark PDF — overlays a diagonal, semi-transparent text watermark
(e.g. "CONFIDENTIAL", "DRAFT") on every page.

Approach: build a one-page watermark PDF in memory with reportlab,
then merge ("stamp") it onto every page of the original PDF using pypdf.
"""

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

from app.utils.file_handler import make_output_path


def _build_watermark_overlay(page_width: float, page_height: float, text: str) -> PdfReader:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    c.saveState()
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.3))  # light gray, 30% opacity
    c.translate(page_width / 2, page_height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()

    c.save()
    buffer.seek(0)
    return PdfReader(buffer)


def add_watermark(input_path: Path, text: str = "CONFIDENTIAL") -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        overlay_reader = _build_watermark_overlay(width, height, text)
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    output_path = make_output_path("watermarked")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path