"""
Redact PDF — permanently removes (blacks out) all occurrences of the
given search text on every page. Unlike a watermark, this actually
deletes the underlying text, not just draws over it.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.utils.file_handler import make_output_path


def redact_pdf(input_path: Path, search_text: str) -> Path:
    if not search_text.strip():
        raise ValueError("Search text for redaction cannot be empty.")

    doc = fitz.open(str(input_path))
    total_matches = 0

    for page in doc:
        matches = page.search_for(search_text)
        for rect in matches:
            page.add_redact_annot(rect, fill=(0, 0, 0))
            total_matches += 1
        page.apply_redactions()

    if total_matches == 0:
        doc.close()
        raise ValueError(f"No occurrences of '{search_text}' were found in this PDF.")

    output_path = make_output_path("redacted")
    doc.save(str(output_path))
    doc.close()

    return output_path