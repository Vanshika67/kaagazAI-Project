"""
PDF to Markdown — extracts text from a PDF and writes it out as a
simple Markdown file, using font size to guess headings vs body text.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.utils.file_handler import make_output_path


def pdf_to_markdown(input_path: Path) -> Path:
    doc = fitz.open(str(input_path))
    lines = []

    sizes = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    sizes.append(round(span["size"]))
    body_size = max(set(sizes), key=sizes.count) if sizes else 12

    for page_num, page in enumerate(doc, start=1):
        lines.append(f"\n<!-- Page {page_num} -->\n")
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(span["text"] for span in line.get("spans", [])).strip()
                if not text:
                    continue

                max_size = max((span["size"] for span in line.get("spans", [])), default=body_size)
                if max_size > body_size * 1.5:
                    lines.append(f"# {text}")
                elif max_size > body_size * 1.2:
                    lines.append(f"## {text}")
                else:
                    lines.append(text)

    doc.close()

    output_path = make_output_path("pdf_to_markdown", suffix=".md")
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return output_path