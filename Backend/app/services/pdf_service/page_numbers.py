"""
Add Page Numbers — stamps a page number (e.g. "3 / 10") onto every page,
at the chosen position.
"""

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from app.utils.file_handler import make_output_path

POSITIONS = {"bottom-center", "bottom-right", "bottom-left"}


def _build_number_overlay(page_width: float, page_height: float, label: str, position: str) -> PdfReader:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    c.setFont("Helvetica", 10)

    margin = 30
    if position == "bottom-center":
        c.drawCentredString(page_width / 2, margin, label)
    elif position == "bottom-right":
        c.drawRightString(page_width - margin, margin, label)
    else:  # bottom-left
        c.drawString(margin, margin, label)

    c.save()
    buffer.seek(0)
    return PdfReader(buffer)


def add_page_numbers(input_path: Path, position: str = "bottom-center") -> Path:
    if position not in POSITIONS:
        raise ValueError(f"Invalid position '{position}'. Choose from {POSITIONS}.")

    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        label = f"{i} / {total_pages}"

        overlay_reader = _build_number_overlay(width, height, label, position)
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    output_path = make_output_path("numbered")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path