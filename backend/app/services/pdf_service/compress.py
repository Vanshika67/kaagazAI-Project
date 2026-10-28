"""
Compress PDF — reduces file size.

Uses Ghostscript when it is installed (best compression).
If Ghostscript is not found (or fails), falls back to PyMuPDF so the
tool still works on any machine, including Windows without Ghostscript.
"""

import shutil
import subprocess
from pathlib import Path

import pymupdf

from app.utils.file_handler import make_output_path

QUALITY_PRESETS = {
    "low": "/screen",     # smallest size, lowest quality
    "medium": "/ebook",   # good balance (default)
    "high": "/printer",   # larger size, better quality
}

# Image quality (JPEG) used by the PyMuPDF fallback
FALLBACK_JPEG_QUALITY = {
    "low": 35,
    "medium": 60,
    "high": 80,
}


def _find_ghostscript():
    """Return the Ghostscript executable path, or None if not installed."""
    return (
        shutil.which("gswin64c")
        or shutil.which("gswin32c")
        or shutil.which("gs")
    )


def _compress_with_ghostscript(gs_exe: str, input_path: Path, output_path: Path, quality: str) -> bool:
    command = [
        gs_exe,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={QUALITY_PRESETS[quality]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except OSError:
        return False
    return result.returncode == 0 and Path(output_path).exists()


def _compress_with_pymupdf(input_path: Path, output_path: Path, quality: str) -> None:
    doc = pymupdf.open(str(input_path))
    try:
        # Re-compress embedded images (works in recent PyMuPDF versions)
        try:
            doc.rewrite_images(
                dpi_threshold=150 if quality != "high" else 200,
                dpi_target=110 if quality == "low" else 130 if quality == "medium" else 170,
                quality=FALLBACK_JPEG_QUALITY[quality],
            )
        except Exception:
            # If image rewriting is unavailable, still do lossless cleanup below
            pass

        doc.save(
            str(output_path),
            garbage=4,      # remove unused objects
            deflate=True,   # compress streams
            clean=True,     # clean content streams
        )
    finally:
        doc.close()


def compress_pdf(input_path: Path, quality: str = "medium") -> Path:
    if quality not in QUALITY_PRESETS:
        raise ValueError(f"Invalid quality '{quality}'. Choose from {list(QUALITY_PRESETS)}.")

    input_path = Path(input_path)
    output_path = Path(make_output_path("compressed"))

    gs_exe = _find_ghostscript()
    if gs_exe and _compress_with_ghostscript(gs_exe, input_path, output_path, quality):
        return output_path

    # Fallback: pure Python (no external program needed)
    _compress_with_pymupdf(input_path, output_path, quality)
    return output_path