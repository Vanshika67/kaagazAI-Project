"""
format_wrapper.py
------------------
Universal layer that lets ANY existing PDF tool (merge, split, compress,
watermark, etc.) accept Word input and/or return Word output, without
rewriting the tool itself.

Flow:
    input file (pdf/doc/docx)
        -> normalize_to_pdf()       [Word -> PDF if needed]
        -> tool_fn(...)             [your existing PDF-only function]
        -> finalize_output()        [PDF -> Word if user asked for Word]
"""

import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Callable, List

from pdf2docx import Converter as PdfToDocxConverter

WORD_EXTENSIONS = (".doc", ".docx")
TEMP_DIR = os.path.abspath(os.environ.get("TEMP_FILES_DIR", "app/temp_files"))

# Common LibreOffice install locations on Windows
_SOFFICE_FALLBACK_PATHS = (
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
)


def _temp_path(suffix: str) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


def _is_word(file_path) -> bool:
    return str(file_path).lower().endswith(WORD_EXTENSIONS)


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


def convert_word_to_pdf(word_path) -> str:
    """Uses LibreOffice headless to convert a Word file to PDF."""
    word_path = str(word_path)
    out_dir = os.path.dirname(word_path) or TEMP_DIR
    soffice = find_soffice()

    # Separate profile folder so a running/locked LibreOffice doesn't block us
    profile_dir = tempfile.mkdtemp(prefix="lo_profile_")
    profile_uri = Path(profile_dir).as_uri()

    try:
        result = subprocess.run(
            [
                soffice,
                f"-env:UserInstallation={profile_uri}",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", out_dir,
                word_path,
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("LibreOffice took too long to convert the file.")
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)

    base = os.path.splitext(os.path.basename(word_path))[0]
    produced = os.path.join(out_dir, f"{base}.pdf")

    if result.returncode != 0 or not os.path.exists(produced):
        details = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"LibreOffice failed to produce PDF output. {details}")

    return produced


def convert_pdf_to_word(pdf_path) -> str:
    """Uses pdf2docx to convert a PDF file to an editable .docx file."""
    out_path = _temp_path(".docx")
    converter = PdfToDocxConverter(str(pdf_path))
    try:
        converter.convert(out_path)
    finally:
        converter.close()
    return out_path


def normalize_to_pdf(file_path) -> str:
    """If the input is Word, convert it to PDF. Otherwise return as-is."""
    if _is_word(file_path):
        return convert_word_to_pdf(file_path)
    return str(file_path)


def normalize_many_to_pdf(file_paths: List) -> List[str]:
    """Same as normalize_to_pdf but for a list (e.g. Merge takes many files)."""
    return [normalize_to_pdf(fp) for fp in file_paths]


def finalize_output(pdf_path, output_format: str) -> str:
    """
    Converts the tool's PDF result into whatever format the user asked for.
    output_format: "pdf" | "word"
    """
    output_format = (output_format or "pdf").lower()
    if output_format in ("word", "docx", "doc"):
        return convert_pdf_to_word(pdf_path)
    return str(pdf_path)


def run_universal_tool(
    input_files,
    output_format: str,
    tool_fn: Callable,
    **tool_kwargs,
):
    """
    Generic wrapper for SINGLE or MULTI file tools.

    input_files    : a single file path OR a list of file paths
    output_format  : "pdf" or "word" — what the user wants back
    tool_fn        : your existing PDF-only function, e.g. merge_pdfs(list) -> pdf_path
                     or compress_pdf(path) -> pdf_path
    tool_kwargs    : any extra arguments tool_fn needs (e.g. rotation angle)

    Returns: path to the final file in the requested format.
    """
    if isinstance(input_files, list):
        normalized = normalize_many_to_pdf(input_files)
        result_pdf = tool_fn(normalized, **tool_kwargs)
    else:
        normalized = normalize_to_pdf(input_files)
        result_pdf = tool_fn(normalized, **tool_kwargs)

    return finalize_output(result_pdf, output_format)