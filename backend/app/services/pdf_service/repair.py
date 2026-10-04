"""
Repair PDF — attempts to fix a corrupted/damaged PDF by having
Ghostscript fully re-write its internal structure.
"""

import subprocess
from pathlib import Path

from app.utils.file_handler import make_output_path


def repair_pdf(input_path: Path) -> Path:
    output_path = make_output_path("repaired")

    command = [
        "gs",
        "-o", str(output_path),
        "-sDEVICE=pdfwrite",
        "-dPDFSETTINGS=/prepress",
        str(input_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not output_path.exists():
        raise RuntimeError(f"Could not repair this PDF: {result.stderr}")

    return output_path