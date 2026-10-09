"""
Office to PDF — converts Word (.docx), Excel (.xlsx), or PowerPoint (.pptx)
files to PDF using LibreOffice in headless mode.
"""

import subprocess
from pathlib import Path

from app.config import TEMP_DIR

ALLOWED_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"}


def office_to_pdf(input_path: Path) -> Path:
    if input_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{input_path.suffix}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    command = [
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", str(TEMP_DIR), str(input_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed: {result.stderr or result.stdout}")

    expected_output = TEMP_DIR / (input_path.stem + ".pdf")
    if not expected_output.exists():
        raise RuntimeError("Conversion completed but the output PDF was not found.")

    return expected_output