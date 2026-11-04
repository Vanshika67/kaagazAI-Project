"""
AI Draft - question se answer ka draft (study / practice ke liye).
Endpoint: POST /api/tools/ai-draft  -> {"draft": "..."}
"""
import json
import os
import urllib.error
import urllib.request

from fastapi import APIRouter, Form, HTTPException

from app.config import GEMINI_API_KEY

router = APIRouter(tags=["AI Draft"])

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

LENGTHS = {
    "short": "about 3-4 lines (2 marks)",
    "medium": "about 8-10 lines (5 marks)",
    "long": "about 15-20 lines (10 marks)",
}


@router.post("/tools/ai-draft")
def ai_draft(
    question: str = Form(...),
    length: str = Form("medium"),
    language: str = Form("English"),
):
    if not GEMINI_API_KEY:
        raise HTTPException(500, ".env mein GEMINI_API_KEY set nahi hai.")
    if not question.strip():
        raise HTTPException(400, "Question khaali hai.")

    size = LENGTHS.get(length, LENGTHS["medium"])
    prompt = (
        "You are helping a student prepare a draft answer for their own assignment.\n"
        f"Write the answer in {language}, length: {size}.\n"
        "Rules: answer only what the question asks, be accurate and clear, "
        "use simple sentences. Plain text only: no markdown, no asterisks, "
        "no # headings. Use short numbered points only if the question needs them.\n\n"
        f"Question:\n{question.strip()}"
    )

    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        URL,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="ignore")[:300]
        raise HTTPException(502, f"Gemini error {e.code}: {detail}")
    except Exception as e:
        raise HTTPException(502, f"Gemini se connect nahi ho paya: {e}")

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise HTTPException(502, "AI ne koi answer nahi diya. Question dobara try karo.")

    return {"draft": text}
