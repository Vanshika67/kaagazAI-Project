"""
resume_builder.py
------------------
Generates a resume as PDF or Word, in one of two styles:
  - "simple": single-column, ATS-friendly, no colors/photo
  - "modern": 2-column, colored sidebar, optional photo
"""

import os
import uuid

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

router = APIRouter()
TEMP_DIR = os.path.abspath("app/temp_files")

ACCENT = HexColor("#4f46e5")   # indigo, matches the app's theme
SIDEBAR_BG = HexColor("#1e1b4b")


def _out(suffix: str) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


def _parse_lines(text: str) -> list[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


# ======================================================================
# SIMPLE PDF (single column, ATS-friendly)
# ======================================================================
def _build_simple_pdf(data: dict) -> str:
    out = _out(".pdf")
    page_w, page_h = A4
    c = canvas.Canvas(out, pagesize=A4)
    x_margin = 20 * mm
    y = page_h - 20 * mm

    def line_break(amount=6 * mm):
        nonlocal y
        y -= amount
        if y < 20 * mm:
            c.showPage()
            y = page_h - 20 * mm

    c.setFont("Helvetica-Bold", 20)
    c.drawString(x_margin, y, data["full_name"])
    line_break(8 * mm)

    c.setFont("Helvetica", 10)
    contact_bits = [data.get("email"), data.get("phone"), data.get("location")]
    c.drawString(x_margin, y, "  |  ".join(b for b in contact_bits if b))
    line_break(10 * mm)
    c.line(x_margin, y, page_w - x_margin, y)
    line_break(8 * mm)

    def section(title: str, body_lines: list[str]):
        nonlocal y
        if not body_lines:
            return
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x_margin, y, title.upper())
        line_break(6 * mm)
        c.setFont("Helvetica", 10)
        for item in body_lines:
            c.drawString(x_margin + 4 * mm, y, f"\u2022 {item}")
            line_break(5.5 * mm)
        line_break(3 * mm)

    if data.get("summary"):
        section("Professional Summary", [data["summary"]])
    section("Education", _parse_lines(data.get("education", "")))
    section("Experience", _parse_lines(data.get("experience", "")))
    section("Skills", _parse_lines(data.get("skills", "")))
    section("Projects", _parse_lines(data.get("projects", "")))
    section("Certifications", _parse_lines(data.get("certifications", "")))

    c.save()
    return out


# ======================================================================
# MODERN PDF (2-column, colored sidebar, optional photo)
# ======================================================================
def _build_modern_pdf(data: dict, photo_path: str | None) -> str:
    out = _out(".pdf")
    page_w, page_h = A4
    c = canvas.Canvas(out, pagesize=A4)

    sidebar_w = 65 * mm
    main_x = sidebar_w + 12 * mm
    main_right = page_w - 15 * mm

    # --- sidebar background ---
    c.setFillColor(SIDEBAR_BG)
    c.rect(0, 0, sidebar_w, page_h, fill=1, stroke=0)

    sb_x = 10 * mm
    sb_y = page_h - 15 * mm

    # --- photo (optional, circular-ish square) ---
    if photo_path:
        try:
            img = ImageReader(photo_path)
            photo_size = 35 * mm
            c.drawImage(
                img, sb_x, sb_y - photo_size, width=photo_size, height=photo_size,
                preserveAspectRatio=True, mask="auto",
            )
            sb_y -= photo_size + 8 * mm
        except Exception:
            pass  # bad image -> just skip, don't fail the whole resume

    # --- name in sidebar ---
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15)
    name_lines = _wrap_text(c, data["full_name"], "Helvetica-Bold", 15, sidebar_w - 2 * sb_x)
    for nl in name_lines:
        c.drawString(sb_x, sb_y, nl)
        sb_y -= 6 * mm
    sb_y -= 4 * mm

    def sidebar_section(title: str, lines: list[str]):
        nonlocal sb_y
        if not lines:
            return
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(sb_x, sb_y, title.upper())
        sb_y -= 5 * mm
        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        for item in lines:
            for wrapped in _wrap_text(c, item, "Helvetica", 9, sidebar_w - 2 * sb_x):
                c.drawString(sb_x, sb_y, wrapped)
                sb_y -= 4.5 * mm
        sb_y -= 4 * mm

    contact_lines = [b for b in [data.get("email"), data.get("phone"), data.get("location")] if b]
    sidebar_section("Contact", contact_lines)
    sidebar_section("Skills", _parse_lines(data.get("skills", "")))
    sidebar_section("Certifications", _parse_lines(data.get("certifications", "")))

    # --- main column ---
    y = page_h - 20 * mm

    def main_section(title: str, body_lines: list[str], as_bullets=True):
        nonlocal y
        if not body_lines:
            return
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(main_x, y, title.upper())
        y -= 2 * mm
        c.setStrokeColor(ACCENT)
        c.line(main_x, y, main_right, y)
        y -= 6 * mm
        c.setFillColor(black)
        c.setFont("Helvetica", 10)
        for item in body_lines:
            prefix = "\u2022 " if as_bullets else ""
            for wrapped in _wrap_text(c, prefix + item, "Helvetica", 10, main_right - main_x):
                if y < 20 * mm:
                    c.showPage()
                    y = page_h - 20 * mm
                c.drawString(main_x, y, wrapped)
                y -= 5.5 * mm
        y -= 4 * mm

    if data.get("summary"):
        main_section("Profile", [data["summary"]], as_bullets=False)
    main_section("Experience", _parse_lines(data.get("experience", "")))
    main_section("Education", _parse_lines(data.get("education", "")))
    main_section("Projects", _parse_lines(data.get("projects", "")))

    c.save()
    return out


def _wrap_text(c: canvas.Canvas, text: str, font: str, size: int, max_width: float) -> list[str]:
    """Simple word-wrap so long lines don't run off the page/sidebar."""
    c.setFont(font, size)
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


# ======================================================================
# WORD (single-column for both styles — Word can't do sidebars reliably)
# ======================================================================
def _build_docx(data: dict, template_style: str) -> str:
    out = _out(".docx")
    doc = Document()

    title = doc.add_heading(data["full_name"], level=0)
    title.runs[0].font.size = Pt(24)
    if template_style == "modern":
        title.runs[0].font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)

    contact_bits = [data.get("email"), data.get("phone"), data.get("location")]
    contact_p = doc.add_paragraph("  |  ".join(b for b in contact_bits if b))
    contact_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    doc.add_paragraph("_" * 60)

    def section(title: str, body_lines: list[str]):
        if not body_lines:
            return
        h = doc.add_heading(title, level=1)
        if template_style == "modern":
            h.runs[0].font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
        for item in body_lines:
            doc.add_paragraph(item, style="List Bullet")

    if data.get("summary"):
        h = doc.add_heading("Professional Summary", level=1)
        if template_style == "modern":
            h.runs[0].font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
        doc.add_paragraph(data["summary"])

    section("Education", _parse_lines(data.get("education", "")))
    section("Experience", _parse_lines(data.get("experience", "")))
    section("Skills", _parse_lines(data.get("skills", "")))
    section("Projects", _parse_lines(data.get("projects", "")))
    section("Certifications", _parse_lines(data.get("certifications", "")))

    doc.save(out)
    return out


# ======================================================================
# Endpoint
# ======================================================================
@router.post("/tools/resume-builder")
async def build_resume(
    full_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    location: str = Form(""),
    summary: str = Form(""),
    education: str = Form(""),
    experience: str = Form(""),
    skills: str = Form(""),
    projects: str = Form(""),
    certifications: str = Form(""),
    output_format: str = Form("pdf"),            # "pdf" | "word"
    template_style: str = Form("simple"),         # "simple" | "modern"
    photo: UploadFile | None = File(None, description="Optional photo, used only by the 'modern' PDF template"),
):
    if not full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required.")
    if template_style not in ("simple", "modern"):
        raise HTTPException(status_code=400, detail="template_style must be 'simple' or 'modern'.")

    data = {
        "full_name": full_name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "location": location.strip(),
        "summary": summary.strip(),
        "education": education,
        "experience": experience,
        "skills": skills,
        "projects": projects,
        "certifications": certifications,
    }

    if output_format == "word":
        out = _build_docx(data, template_style)
        return FileResponse(out, filename=f"resume_{template_style}.docx")

    if template_style == "modern":
        photo_path = None
        if photo is not None and photo.filename:
            os.makedirs(TEMP_DIR, exist_ok=True)
            ext = os.path.splitext(photo.filename)[1] or ".jpg"
            photo_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")
            with open(photo_path, "wb") as f:
                f.write(await photo.read())
        out = _build_modern_pdf(data, photo_path)
    else:
        out = _build_simple_pdf(data)

    return FileResponse(out, filename=f"resume_{template_style}.pdf")