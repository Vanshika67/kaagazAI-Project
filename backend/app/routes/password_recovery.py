"""
password_recovery.py
---------------------
Best-effort password recovery for PDF, Word, Excel, PowerPoint files
you own but forgot the password to. Tries passwords from a wordlist
and/or a digit-only brute force within a safety limit — it cannot
break a strong/long password, only recover weak or partially-known ones.
"""

import itertools
import os
import shutil
import string
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter()
TEMP_DIR = os.path.abspath("app/temp_files")

OFFICE_EXT = (".docx", ".xlsx", ".pptx")
MAX_ATTEMPTS_HARD_LIMIT = 200_000  # safety cap so the server never hangs forever


def _save(upload: UploadFile) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    ext = os.path.splitext(upload.filename or "")[1]
    path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


def _out(suffix: str) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


def _candidates(wordlist_text: str | None, charset: str, min_len: int, max_len: int, max_attempts: int):
    """Yield candidate passwords: wordlist entries first, then brute force."""
    seen = set()
    if wordlist_text:
        for line in wordlist_text.splitlines():
            pw = line.strip()
            if pw and pw not in seen:
                seen.add(pw)
                yield pw

    if charset and max_len:
        count = 0
        for length in range(max(min_len, 1), max_len + 1):
            for combo in itertools.product(charset, repeat=length):
                pw = "".join(combo)
                if pw in seen:
                    continue
                yield pw
                count += 1
                if count >= max_attempts:
                    return


def _try_pdf(path: str, passwords):
    import pikepdf

    for pw in passwords:
        try:
            with pikepdf.open(path, password=pw) as pdf:
                out = _out(".pdf")
                pdf.save(out)
                return out, pw
        except pikepdf.PasswordError:
            continue
    return None, None


def _try_office(path: str, ext: str, passwords):
    import msoffcrypto

    for pw in passwords:
        try:
            with open(path, "rb") as f_in:
                office = msoffcrypto.OfficeFile(f_in)
                office.load_key(password=pw)
                out = _out(ext)
                with open(out, "wb") as f_out:
                    office.decrypt(f_out)
                return out, pw
        except Exception:
            continue
    return None, None


@router.post("/security/crack-password")
async def crack_password(
    file: UploadFile = File(...),
    wordlist: UploadFile | None = File(None, description="Optional .txt file, one password per line"),
    use_digits_bruteforce: bool = Form(False, description="Try all-digit passwords too (slow)"),
    min_length: int = Form(4),
    max_length: int = Form(6),
    max_attempts: int = Form(20000),
):
    name = file.filename or "file"
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if ext not in (".pdf",) + OFFICE_EXT:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, XLSX or PPTX files are supported.",
        )

    src = _save(file)

    wordlist_text = None
    if wordlist is not None:
        wordlist_text = (await wordlist.read()).decode("utf-8", errors="ignore")

    max_attempts = min(max_attempts, MAX_ATTEMPTS_HARD_LIMIT)
    charset = string.digits if use_digits_bruteforce else ""
    candidates = _candidates(wordlist_text, charset, min_length, max_length, max_attempts)

    if ext == ".pdf":
        out, found_pw = _try_pdf(src, candidates)
    else:
        out, found_pw = _try_office(src, ext, candidates)

    if out is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Could not recover the password within the attempts given. "
                "Try a bigger wordlist, or increase max_length / max_attempts "
                "(this will take longer)."
            ),
        )

    return FileResponse(
        out,
        filename=f"{stem}_unlocked{ext}",
        headers={"X-Recovered-Password": found_pw},
    )