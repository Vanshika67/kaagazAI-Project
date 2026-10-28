"""
document_service.py
--------------------
Generates formatted documents (ID-card style layouts, marksheets, etc.)
from user-entered field data, as PDF or Word.

Uses reportlab (pure Python, no system dependencies) instead of
WeasyPrint, since WeasyPrint needs GTK libraries that are painful to
install on Windows.

IMPORTANT (keep this in the product too):
These templates are generic "document card" layouts for practice /
sample / learning purposes (e.g. mock marksheets, demo ID cards for a
college project). They must NOT reproduce real government seals, logos,
or official formats, and every generated file is watermarked
"SAMPLE / NOT A GOVERNMENT DOCUMENT" to avoid misuse for fake ID
creation.
"""

import os
import uuid
from typing import Dict, List

from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

TEMP_DIR = "app/temp_files"

TEMPLATE_TITLES: Dict[str, str] = {
    "generic_id_card": "ID Card (Sample)",
    "marksheet": "Statement of Marks (Sample)",
}


def _draw_watermark(c: canvas.Canvas, width: float, height: float):
    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(colors.Color(0.8, 0, 0, alpha=0.15))
    c.translate(width / 2, height / 2)
    c.rotate(30)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()


def _draw_footer_disclaimer(c: canvas.Canvas, width: float):
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.grey)
    c.drawCentredString(
        width / 2, 15,
        "This is a sample document generated for demonstration purposes only. "
        "Not a valid government or official document.",
    )


def _draw_generic_id_card(c: canvas.Canvas, document_title: str, fields: List[dict]):
    width, height = 90 * mm, 55 * mm
    c.setPageSize((width, height))

    _draw_watermark(c, width, height)

    c.setStrokeColor(colors.black)
    c.setLineWidth(1.2)
    c.roundRect(3, 3, width - 6, height - 6, 6, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(10, height - 16, document_title)

    c.setFont("Helvetica", 9)
    y = height - 28
    for field in fields:
        c.drawString(10, y, f"{field['label']}: {field['value']}")
        y -= 11
        if y < 10:
            break

    _draw_footer_disclaimer(c, width)
    c.showPage()


def _draw_marksheet(c: canvas.Canvas, document_title: str, fields: List[dict]):
    width, height = A4
    c.setPageSize(A4)

    _draw_watermark(c, width, height)

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 60, document_title)

    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 80, "Statement of Marks")

    c.setStrokeColor(colors.grey)
    c.rect(50, height - 420, width - 100, 320, stroke=1, fill=0)

    c.setFont("Helvetica", 11)
    y = height - 140
    for field in fields:
        c.drawString(70, y, f"{field['label']}:")
        c.drawString(220, y, str(field["value"]))
        c.line(70, y - 4, width - 70, y - 4)
        y -= 24
        if y < height - 400:
            break

    _draw_footer_disclaimer(c, width)
    c.showPage()


def generate_document_pdf(template_key: str, document_title: str, fields: list) -> str:
    if template_key not in TEMPLATE_TITLES:
        raise ValueError(f"Unknown template '{template_key}'. Options: {list(TEMPLATE_TITLES)}")

    os.makedirs(TEMP_DIR, exist_ok=True)
    out_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_{template_key}.pdf")
    c = canvas.Canvas(out_path)

    if template_key == "generic_id_card":
        _draw_generic_id_card(c, document_title, fields)
    elif template_key == "marksheet":
        _draw_marksheet(c, document_title, fields)

    c.save()
    return out_path


def generate_document_word(template_key: str, document_title: str, fields: list) -> str:
    if template_key not in TEMPLATE_TITLES:
        raise ValueError(f"Unknown template '{template_key}'. Options: {list(TEMPLATE_TITLES)}")

    os.makedirs(TEMP_DIR, exist_ok=True)
    doc = Document()

    doc.add_heading(document_title, level=1)
    doc.add_paragraph("SAMPLE — Not a government or official document.").italic = True

    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for field in fields:
        row = table.add_row().cells
        row[0].text = field["label"]
        row[1].text = str(field["value"])

    footer = doc.add_paragraph(
        "This is a sample document generated for demonstration purposes only."
    )
    for run in footer.runs:
        run.font.size = Pt(8)

    out_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_{template_key}.docx")
    doc.save(out_path)
    return out_path


def generate_document(template_key: str, document_title: str, fields: list, output_format: str) -> str:
    if output_format.lower() in ("word", "docx", "doc"):
        return generate_document_word(template_key, document_title, fields)
    return generate_document_pdf(template_key, document_title, fields)