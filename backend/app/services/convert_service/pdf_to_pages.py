"""
pdf_to_pages.py
----------------
Converts every page of a PDF into a separate image, then zips them.
Add this as a new "Convert" tool: PDF -> Pages (Images).
"""

import os
import uuid
import zipfile

import fitz  # PyMuPDF

TEMP_DIR = "app/temp_files"


def pdf_to_pages(pdf_path: str, image_format: str = "png", dpi: int = 150) -> str:
    """
    Renders each page of the PDF as an image and returns a path to a
    zip file containing all the page images.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    job_id = uuid.uuid4().hex
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    zoom = dpi / 72  # PyMuPDF default is 72 dpi
    matrix = fitz.Matrix(zoom, zoom)

    image_paths = []
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(matrix=matrix)
        img_path = os.path.join(
            job_dir, f"page_{page_number + 1}.{image_format}"
        )
        pix.save(img_path)
        image_paths.append(img_path)
    doc.close()

    zip_path = os.path.join(TEMP_DIR, f"{job_id}_pages.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for img_path in image_paths:
            zf.write(img_path, arcname=os.path.basename(img_path))

    return zip_path