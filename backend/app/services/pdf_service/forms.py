"""
PDF Forms — reads the fillable field names from a PDF form, and can
fill them in with provided values (for AcroForm-based PDFs).
"""

from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def get_form_fields(input_path: Path) -> List[str]:
    reader = PdfReader(str(input_path))
    fields = reader.get_fields()
    if not fields:
        return []
    return list(fields.keys())


def fill_form(input_path: Path, field_values: Dict[str, str]) -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    writer.append(reader)

    if not reader.get_fields():
        raise ValueError("This PDF has no fillable form fields.")

    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    output_path = make_output_path("filled_form")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path