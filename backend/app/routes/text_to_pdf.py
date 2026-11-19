"""
Text to PDF - plain text (kitni bhi lines) ko PDF mein convert karta hai.
Endpoint: POST /api/text-to-pdf
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from starlette.background import BackgroundTask

router = APIRouter(tags=["Text to PDF"])

BASE = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE / "temp_files"


def _wrap(text, font, size, max_width):
    lines = []
    for para in text.replace("\r", "").split("\n"):
        if not para.strip():
            lines.append("")
            continue
        current = ""
        for word in para.split():
            trial = (current + " " + word).strip()
            if stringWidth(trial, font, size) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


@router.post("/text-to-pdf")
def text_to_pdf(
    text: str = Form(...),
    title: str = Form(""),
    font_size: str = Form("12"),
    line_spacing: str = Form("1.4"),
):
    if not text.strip():
        raise HTTPException(400, "Text khaali hai.")

    try:
        size = max(8, min(28, float(font_size)))
    except ValueError:
        size = 12
    try:
        spacing = max(1.0, min(2.5, float(line_spacing)))
    except ValueError:
        spacing = 1.4

    page_w, page_h = A4
    margin = 50
    font = "Helvetica"
    line_h = size * spacing
    usable_h = page_h - 2 * margin
    per_page = max(1, int(usable_h // line_h))

    lines = _wrap(text, font, size, page_w - 2 * margin)

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    out_path = TEMP_DIR / (uid + "_text.pdf")

    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle(title or "Text Document")

    start_idx = 0
    page_num = 1
    while start_idx < len(lines) or page_num == 1:
        top = page_h - margin
        if title and page_num == 1:
            c.setFont("Helvetica-Bold", size + 4)
            c.drawString(margin, top, title)
            top -= (size + 4) * spacing * 1.3

        chunk = lines[start_idx:start_idx + per_page]
        c.setFont(font, size)
        for i, ln in enumerate(chunk):
            c.drawString(margin, top - i * line_h, ln)

        c.setFont("Helvetica", 8)
        c.drawCentredString(page_w / 2, 20, "Page " + str(page_num))
        c.showPage()

        start_idx += len(chunk) if chunk else per_page
        page_num += 1
        if not chunk and start_idx >= len(lines):
            break

    c.save()

    def _delete():
        try:
            out_path.unlink(missing_ok=True)
        except OSError:
            pass

    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename="text_to_pdf.pdf",
        background=BackgroundTask(_delete),
    )
