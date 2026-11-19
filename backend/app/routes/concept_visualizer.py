"""
Concept Visualizer - PDF ya text se AI topic + branches nikalta hai aur
ek mind-map jaisi diagram PDF banata hai.
Endpoint: POST /api/tools/concept-visualizer
"""
import json
import os
import re
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from starlette.background import BackgroundTask

from app.config import GEMINI_API_KEY

router = APIRouter(tags=["Concept Visualizer"])

BASE = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE / "temp_files"

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

PALETTE = ["#4f46e5", "#0ea5e9", "#059669", "#d97706", "#db2777", "#7c3aed", "#0891b2", "#ea580c"]


def _wrap(text, font, size, max_width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _ask_gemini(source_text: str, max_branches: int) -> dict:
    prompt = (
        "You will read the text below and extract its mind-map structure.\n"
        f"Return STRICT JSON only, no markdown fences, no extra words, in this shape:\n"
        '{"topic": "short central topic (max 5 words)", '
        '"branches": [{"name": "short branch title (max 4 words)", '
        '"points": ["short point", "short point", "short point"]}]}\n'
        f"Give at most {max_branches} branches, each with 2 to 4 short points "
        "(max 6 words each). Keep everything concise.\n\nText:\n" + source_text[:12000]
    )
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        URL, data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"Gemini error {e.code}: {e.read().decode(errors='ignore')[:300]}")
    except Exception as e:
        raise HTTPException(502, f"Gemini se connect nahi ho paya: {e}")

    try:
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise HTTPException(502, "AI ne koi structure nahi diya.")

    raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(502, "AI ka output JSON mein parse nahi ho paya. Dobara try karo.")
    return parsed


@router.post("/tools/concept-visualizer")
async def concept_visualizer(
    text: str = Form(""),
    max_branches: str = Form("6"),
    file: UploadFile | None = File(None),
):
    if not GEMINI_API_KEY:
        raise HTTPException(500, ".env mein GEMINI_API_KEY set nahi hai.")

    source_text = text.strip()
    if file is not None and file.filename:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "File sirf .pdf honi chahiye.")
        data = await file.read()
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = TEMP_DIR / f"{uuid.uuid4().hex}_cv.pdf"
        tmp.write_bytes(data)
        try:
            reader = PdfReader(str(tmp))
            source_text = "\n".join((p.extract_text() or "") for p in reader.pages)
        finally:
            tmp.unlink(missing_ok=True)

    if not source_text.strip():
        raise HTTPException(400, "Text daalo ya ek text-based PDF upload karo.")

    try:
        branches_n = max(2, min(8, int(max_branches)))
    except ValueError:
        branches_n = 6

    structure = _ask_gemini(source_text, branches_n)
    topic = structure.get("topic", "Topic")
    branches = structure.get("branches", [])[:branches_n]
    if not branches:
        raise HTTPException(502, "AI ko koi branches nahi mile. Zyada text ke saath try karo.")

    # ---- draw mind map ----
    page_w, page_h = landscape(A4)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    out_path = TEMP_DIR / f"{uid}_conceptmap.pdf"
    c = canvas.Canvas(str(out_path), pagesize=landscape(A4))
    c.setTitle(f"Concept map: {topic}")

    cols = 3 if len(branches) > 4 else 2
    rows = -(-len(branches) // cols)
    box_w, box_h = 200, 95
    margin_x, margin_y = 40, 70
    grid_w = page_w - 2 * margin_x
    grid_h = page_h - margin_y - 150
    gap_x = (grid_w - cols * box_w) / max(1, cols - 1) if cols > 1 else 0
    gap_y = (grid_h - rows * box_h) / max(1, rows - 1) if rows > 1 else 0

    center_x, center_y = page_w / 2, page_h - 55
    c.setFillColor(HexColor("#1e1b4b"))
    c.roundRect(center_x - 140, center_y - 24, 280, 48, 10, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(center_x, center_y - 6, topic[:40])

    for i, br in enumerate(branches):
        row, col = divmod(i, cols)
        bx = margin_x + col * (box_w + gap_x)
        by = page_h - 150 - row * (box_h + gap_y) - box_h
        color = HexColor(PALETTE[i % len(PALETTE)])

        c.setStrokeColor(color)
        c.setLineWidth(1.5)
        c.line(center_x, center_y - 24, bx + box_w / 2, by + box_h)

        c.setFillColor(color)
        c.roundRect(bx, by + box_h - 26, box_w, 26, 6, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(bx + box_w / 2, by + box_h - 18, (br.get("name", "")[:30]))

        c.setFillColor(HexColor("#f8fafc"))
        c.rect(bx, by, box_w, box_h - 26, fill=1, stroke=0)
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.rect(bx, by, box_w, box_h, fill=0, stroke=1)

        c.setFillColor(HexColor("#1e293b"))
        c.setFont("Helvetica", 8)
        ty = by + box_h - 38
        for pt in br.get("points", [])[:4]:
            for ln in _wrap("\u2022 " + pt, "Helvetica", 8, box_w - 16)[:2]:
                c.drawString(bx + 8, ty, ln)
                ty -= 11

    c.showPage()
    c.save()

    def _delete():
        out_path.unlink(missing_ok=True)

    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename="concept_map.pdf",
        background=BackgroundTask(_delete),
    )