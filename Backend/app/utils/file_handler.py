"""
Utility functions shared by every PDF tool:
- saving an uploaded file to the temp folder
- generating unique output filenames
- deleting old temp files (privacy / disk-space cleanup)
"""

import time
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import TEMP_DIR, MAX_FILE_SIZE_MB, FILE_RETENTION_MINUTES


def save_upload(file: UploadFile) -> Path:
    """
    Saves an uploaded file into the temp folder with a unique name
    and returns its path. Rejects the file if it's not a PDF or if
    it's larger than the configured limit.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed is {MAX_FILE_SIZE_MB} MB.",
        )

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = TEMP_DIR / unique_name

    with open(dest_path, "wb") as f:
        f.write(contents)

    return dest_path


def make_output_path(prefix: str, suffix: str = ".pdf") -> Path:
    """Generates a unique path in the temp folder for a tool's output file."""
    unique_name = f"{prefix}_{uuid.uuid4().hex}{suffix}"
    return TEMP_DIR / unique_name


def cleanup_old_files() -> int:
    """
    Deletes temp files older than FILE_RETENTION_MINUTES.
    Call this periodically to keep the server's disk clean and protect
    user privacy. Returns the number of files deleted.
    """
    cutoff = time.time() - (FILE_RETENTION_MINUTES * 60)
    deleted = 0
    for file_path in TEMP_DIR.glob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff:
            file_path.unlink(missing_ok=True)
            deleted += 1
    return deleted