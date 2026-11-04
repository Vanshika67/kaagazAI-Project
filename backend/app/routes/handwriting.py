"""
Handwriting Notes - apne handwriting font mein ruled-page PDF.
Endpoint: POST /api/tools/handwriting
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from starlette.background import BackgroundTask

router = APIRouter(tags=["Handwriting Notes"])

BASE = Path(__file__).resolve().parent.parent          # backend/app
TEMP_DIR = BASE / "temp_files"
DEFAULT_FONT = BASE / "assets" / "fonts" / "default.ttf"  # optional
MAX_FONT_BYTES = 5 * 1024 * 1024

INK = {"blue": "#1a237e", "black": "#111111", "dark_blue": "#0d1b5e"}
LABEL = "Generated with KaagazAI Handwriting Notes"


def _num(value: str, default: float, lo: float, hi: float) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def _wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    for para in text.replace("\r", "").split("\n"):
        if not para.strip():
            lines.append("")
            continue
        current = ""
        for word in para.split():
            trial = f"{current} {word}".strip()
            if pdfmetrics.stringWidth(trial, font, size) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


@router.post("/tools/handwriting")
async def handwriting_pdf(
    text: str = Form(...),
    font: UploadFile | None = File(None),
    font_size: str = Form("18"),
    line_spacing: str = Form("1.6"),
    margin: str = Form("50"),
    max_pages: str = Form(""),
    ink: str = Form("blue"),
    ruled: str = Form("yes"),
):
    if not text.strip():
        raise HTTPException(400, "Text khaali hai.")

    size = _num(font_size, 18, 10, 40)
    spacing = _num(line_spacing, 1.6, 1.2, 3.0)
    m = _num(margin, 50, 20, 120)
    limit = int(_num(max_pages, 0, 0, 200))  # 0 = no limit
    color = HexColor(INK.get(ink, INK["blue"]))

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    cleanup = []

    # ---- font ----
    font_name = "Helvetica"
    font_path = None
    if font is not None and font.filename:
        if not font.filename.lower().endswith((".ttf", ".otf")):
            raise HTTPException(400, "Font .ttf ya .otf file honi chahiye.")
        data = await font.read()
        if len(data) > MAX_FONT_BYTES:
            raise HTTPException(400, "Font file 5 MB se chhoti honi chahiye.")
        font_path = TEMP_DIR / f"{uid}_font.ttf"
        font_path.write_bytes(data)
        cleanup.append(font_path)
    elif DEFAULT_FONT.exists():
        font_path = DEFAULT_FONT

    if font_path:
        try:
            font_name = f"HW_{uid}"
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        except Exception:
            raise HTTPException(400, "Ye font file read nahi ho paayi. Dusri .ttf try karo.")

    # ---- layout ----
    page_w, page_h = A4
    footer_space = 24
    line_h = size * spacing
    usable_h = page_h - 2 * m - footer_space
    per_page = max(1, int(usable_h // line_h))

    lines = _wrap(text, font_name, size, page_w - 2 * m)
    pages_needed = -(-len(lines) // per_page)
    if limit and pages_needed > limit:
        raise HTTPException(
            400,
            f"Text ko {pages_needed} pages chahiye, aapne limit {limit} rakhi hai. "
            "Text kam karo, font size ghatao ya line spacing kam karo.",
        )

    # ---- draw ----
    out_path = TEMP_DIR / f"{uid}_handwriting.pdf"
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle("Handwriting Notes")

    for p in range(pages_needed):
        chunk = lines[p * per_page:(p + 1) * per_page]
        top = page_h - m
        if ruled == "yes":
            c.setStrokeColor(HexColor("#cfd8ec"))
            c.setLineWidth(0.5)
            for i in range(per_page):
                y = top - (i + 1) * line_h + size * 0.25
                c.line(m, y, page_w - m, y)
            c.setStrokeColor(HexColor("#e57373"))
            c.line(m - 10, page_h - m + 10, m - 10, m + footer_space)

        c.setFillColor(color)
        c.setFont(font_name, size)
        for i, ln in enumerate(chunk):
            c.drawString(m, top - (i + 1) * line_h + size * 0.35, ln)

        c.setFillColor(HexColor("#9e9e9e"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(page_w / 2, 14, f"{LABEL}  |  Page {p + 1}/{pages_needed}")
        c.showPage()

    c.save()
    cleanup.append(out_path)

    def _delete():
        for f in cleanup:
            try:
                os.remove(f)
            except OSError:
                pass

    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename="handwriting_notes.pdf",
        background=BackgroundTask(_delete),
    )