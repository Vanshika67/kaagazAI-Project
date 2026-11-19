"""
Voice to Notes - audio file ko AI se transcript + bullet-point notes
banakar PDF deta hai.
Endpoint: POST /api/tools/voice-to-notes
"""
import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from starlette.background import BackgroundTask

from app.config import GEMINI_API_KEY

router = APIRouter(tags=["Voice to Notes"])

BASE = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE / "temp_files"
MAX_AUDIO_MB = 15

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

ALLOWED_EXT = {".mp3": "audio/mp3", ".wav": "audio/wav", ".m4a": "audio/mp4",
               ".ogg": "audio/ogg", ".flac": "audio/flac", ".aac": "audio/aac"}


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


@router.post("/tools/voice-to-notes")
async def voice_to_notes(
    language: str = Form("English"),
    note_style: str = Form("bullet"),
    file: UploadFile = File(...),
):
    if not GEMINI_API_KEY:
        raise HTTPException(500, ".env mein GEMINI_API_KEY set nahi hai.")

    ext = Path(file.filename or "").suffix.lower()
    mime = ALLOWED_EXT.get(ext) or mimetypes.guess_type(file.filename or "")[0]
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, f"Audio format .{ext.strip('.')} supported nahi hai. "
                                  f"Use karo: {', '.join(ALLOWED_EXT)}")

    data = await file.read()
    if len(data) > MAX_AUDIO_MB * 1024 * 1024:
        raise HTTPException(400, f"Audio file {MAX_AUDIO_MB} MB se chhoti honi chahiye.")

    style_line = (
        "short bullet-point notes" if note_style == "bullet" else
        "a short paragraph summary" if note_style == "summary" else
        "the full word-for-word transcript"
    )
    prompt = (
        "Listen to this audio and respond in two clearly separated parts, "
        "written in plain text (no markdown symbols):\n"
        "TRANSCRIPT:\n<the full transcript of what is said>\n\n"
        "NOTES:\n<" + style_line + f", written in {language}>"
    )

    audio_b64 = base64.b64encode(data).decode()
    body = json.dumps({
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": mime, "data": audio_b64}},
        ]}]
    }).encode()
    req = urllib.request.Request(
        URL, data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"Gemini error {e.code}: {e.read().decode(errors='ignore')[:300]}")
    except Exception as e:
        raise HTTPException(502, f"Gemini se connect nahi ho paya: {e}")

    try:
        text_out = result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise HTTPException(502, "AI ne koi jawab nahi diya. Dobara try karo.")

    transcript, notes = text_out, ""
    if "NOTES:" in text_out:
        before, after = text_out.split("NOTES:", 1)
        transcript = before.replace("TRANSCRIPT:", "").strip()
        notes = after.strip()

    # ---- build PDF ----
    page_w, page_h = A4
    margin = 55
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    out_path = TEMP_DIR / f"{uid}_voice_notes.pdf"
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle("Voice to Notes")

    def write_section(heading, body, y, page_num):
        c.setFillColor(HexColor("#4f46e5"))
        c.setFont("Helvetica-Bold", 15)
        c.drawString(margin, y, heading)
        y -= 24
        c.setFillColor(HexColor("#1e293b"))
        c.setFont("Helvetica", 11)
        for ln in _wrap(body, "Helvetica", 11, page_w - 2 * margin):
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
        return y, page_num

    page_num = 1
    y = page_h - margin
    if notes:
        y, page_num = write_section("Notes", notes, y, page_num)
        y -= 20
    y, page_num = write_section("Full transcript", transcript or "(empty)", y, page_num)

    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#94a3b8"))
    c.drawCentredString(page_w / 2, 25, f"Page {page_num}")
    c.showPage()
    c.save()

    def _delete():
        out_path.unlink(missing_ok=True)

    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename="voice_notes.pdf",
        background=BackgroundTask(_delete),
    )