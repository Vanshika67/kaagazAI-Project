"""
Office to PDF — converts Word (.docx), Excel (.xlsx), or PowerPoint (.pptx)
files to PDF using LibreOffice in headless mode.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config import TEMP_DIR

ALLOWED_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"}

# Common LibreOffice install locations on Windows
_SOFFICE_FALLBACK_PATHS = (
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
)


def find_soffice() -> str:
    """Find the LibreOffice executable, even if it is not in PATH."""
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if exe:
        return exe
    for p in _SOFFICE_FALLBACK_PATHS:
        if Path(p).exists():
            return p
    raise RuntimeError(
        "LibreOffice is not installed. Install it from libreoffice.org "
        "to convert Word/Excel/PowerPoint files."
    )


def office_to_pdf(input_path: Path) -> Path:
    input_path = Path(input_path)
    out_dir = Path(TEMP_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    if input_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{input_path.suffix}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    soffice = find_soffice()

    # Separate profile folder so a running/locked LibreOffice doesn't block us
    profile_dir = tempfile.mkdtemp(prefix="lo_profile_")
    profile_uri = Path(profile_dir).as_uri()

    command = [
        soffice,
        f"-env:UserInstallation={profile_uri}",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(input_path),
    ]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=180
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("LibreOffice took too long to convert the file.")
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)

    expected_output = out_dir / (input_path.stem + ".pdf")

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed: {result.stderr or result.stdout}"
        )
    if not expected_output.exists():
        raise RuntimeError("Conversion completed but the output PDF was not found.")

    return expected_output