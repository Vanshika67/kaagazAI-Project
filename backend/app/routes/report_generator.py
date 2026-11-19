"""
Report Generator - title + sections se cover-page wali formatted report PDF.
Endpoint: POST /api/tools/report-generator
Content format: "# Heading" se naya section shuru hota hai, baaki lines us
section ka paragraph text hain.
"""
import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from starlette.background import BackgroundTask

router = APIRouter(tags=["Report Generator"])

BASE = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE / "temp_files"
ACCENT = HexColor("#4f46e5")


def _parse_sections(content: str):
    sections, current = [], None
    for raw in content.replace("\r", "").split("\n"):
        line = raw.rstrip()
        if line.startswith("# "):
            current = {"heading": line[2:].strip(), "body": []}
            sections.append(current)
        elif current is not None:
            current["body"].append(line)
        elif line.strip():
            current = {"heading": "", "body": [line]}
            sections.append(current)
    return sections


def _wrap(text, font, size, max_width):
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        cur = ""
        for word in para.split():
            trial = (cur + " " + word).strip()
            if stringWidth(trial, font, size) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


@router.post("/tools/report-generator")
def report_generator(
    title: str = Form(...),
    author: str = Form(""),
    content: str = Form(...),
):
    if not content.strip():
        raise HTTPException(400, "Report ka content khaali hai.")

    sections = _parse_sections(content)
    if not sections:
        raise HTTPException(400, "Kam se kam ek '# Heading' wala section likho.")

    page_w, page_h = A4
    margin = 55

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    out_path = TEMP_DIR / f"{uid}_report.pdf"
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle(title)

    # ---- cover page ----
    c.setFillColor(ACCENT)
    c.rect(0, page_h - 220, page_w, 220, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 26)
    for i, ln in enumerate(_wrap(title, "Helvetica-Bold", 26, page_w - 2 * margin)):
        c.drawString(margin, page_h - 100 - i * 32, ln)
    c.setFont("Helvetica", 12)
    if author:
        c.drawString(margin, page_h - 250, f"Prepared by: {author}")
    c.drawString(margin, page_h - 270, f"Date: {date.today().strftime('%d %b %Y')}")

    c.setFillColor(HexColor("#1e293b"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, page_h - 330, "Contents")
    c.setFont("Helvetica", 11)
    for i, s in enumerate(sections, 1):
        c.drawString(margin, page_h - 330 - i * 20, f"{i}. {s['heading'] or 'Section'}")
    c.showPage()

    # ---- content pages ----
    page_num = 2
    for idx, s in enumerate(sections, 1):
        y = page_h - margin
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 15)
        heading = f"{idx}. {s['heading']}" if s["heading"] else f"{idx}."
        c.drawString(margin, y, heading)
        y -= 26
        c.setFillColor(HexColor("#1e293b"))
        c.setFont("Helvetica", 11)
        body_text = "\n".join(s["body"]).strip()
        for ln in _wrap(body_text, "Helvetica", 11, page_w - 2 * margin):
            if y < margin + 20:
                c.setFont("Helvetica", 8)
                c.setFillColor(HexColor("#94a3b8"))
                c.drawCentredString(page_w / 2, 25, f"Page {page_num}")
                c.showPage()
                page_num += 1
                y = page_h - margin
                c.setFillColor(HexColor("#1e293b"))
                c.setFont("Helvetica", 11)
            c.drawString(margin, y, ln)
            y -= 16
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#94a3b8"))
        c.drawCentredString(page_w / 2, 25, f"Page {page_num}")
        c.showPage()
        page_num += 1

    c.save()

    def _delete():
        out_path.unlink(missing_ok=True)

    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename="report.pdf",
        background=BackgroundTask(_delete),
    )