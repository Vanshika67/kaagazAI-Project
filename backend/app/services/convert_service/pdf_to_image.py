"""
PDF to Image — renders every page of a PDF as a separate PNG image,
returned zipped together.
"""

import zipfile
from pathlib import Path

import fitz  # PyMuPDF

from app.utils.file_handler import make_output_path


def pdf_to_images(input_path: Path, dpi: int = 150) -> Path:
    doc = fitz.open(str(input_path))
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    image_paths = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix)
        img_path = make_output_path(f"page_{i}", suffix=".png")
        pix.save(str(img_path))
        image_paths.append(img_path)

    doc.close()
    

    zip_path = make_output_path("pdf_to_images", suffix=".zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for img_path in image_paths:
            zipf.write(img_path, arcname=img_path.name)
            img_path.unlink()

    return zip_path