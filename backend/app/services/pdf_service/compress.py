"""
Compress PDF — reduces file size using Ghostscript.
Requires Ghostscript to be installed on the system (`gs` command available).
"""

import subprocess
from pathlib import Path

from app.utils.file_handler import make_output_path

QUALITY_PRESETS = {
    "low": "/screen",     # smallest size, lowest quality
    "medium": "/ebook",   # good balance (default)
    "high": "/printer",   # larger size, better quality
}


def compress_pdf(input_path: Path, quality: str = "medium") -> Path:
    if quality not in QUALITY_PRESETS:
        raise ValueError(f"Invalid quality '{quality}'. Choose from {list(QUALITY_PRESETS)}.")

    output_path = make_output_path("compressed")

    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={QUALITY_PRESETS[quality]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ghostscript compression failed: {result.stderr}")

    return output_path