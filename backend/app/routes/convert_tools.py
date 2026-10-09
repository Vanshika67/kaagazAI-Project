"""
API routes for the Conversion module (Word/Excel/PPT/Image/HTML/Markdown <-> PDF).
"""

import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.config import TEMP_DIR, MAX_FILE_SIZE_MB
from app.utils.file_handler import save_upload
from app.services.convert_service.image_pdf import images_to_pdf
from app.services.convert_service.pdf_to_image import pdf_to_images
from app.services.convert_service.office_pdf import office_to_pdf
from app.services.convert_service.html_pdf import html_to_pdf, pdf_to_html
from app.services.convert_service.pdf_to_markdown import pdf_to_markdown
from app.services.convert_service.scan import scan_to_pdf

router = APIRouter(prefix="/api/convert", tags=["Conversion Tools"])


def _save_any_upload(file: UploadFile) -> Path:
    """Like save_upload, but allows non-PDF files too (images, office docs)."""
    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed is {MAX_FILE_SIZE_MB} MB.",
        )

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = TEMP_DIR / unique_name
    with open(dest_path, "wb") as f:
        f.write(contents)
    return dest_path


@router.post("/images-to-pdf")
async def images_to_pdf_endpoint(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least 1 image.")

    saved_paths = [_save_any_upload(f) for f in files]

    try:
        output_path = images_to_pdf(saved_paths)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="images_to_pdf.pdf")


@router.post("/pdf-to-images")
async def pdf_to_images_endpoint(
    file: UploadFile = File(...),
    dpi: int = Form(150),
):
    saved_path = save_upload(file)

    try:
        output_path = pdf_to_images(saved_path, dpi)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type="application/zip", filename="pdf_to_images.zip")


@router.post("/office-to-pdf")
async def office_to_pdf_endpoint(file: UploadFile = File(...)):
    saved_path = _save_any_upload(file)

    try:
        output_path = office_to_pdf(saved_path)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="converted.pdf")


@router.post("/html-to-pdf")
async def html_to_pdf_endpoint(html_content: str = Form(...)):
    try:
        output_path = html_to_pdf(html_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="html_to_pdf.pdf")


@router.post("/pdf-to-html")
async def pdf_to_html_endpoint(file: UploadFile = File(...)):
    saved_path = save_upload(file)

    try:
        output_path = pdf_to_html(saved_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type="text/html", filename="converted.html")


@router.post("/pdf-to-markdown")
async def pdf_to_markdown_endpoint(file: UploadFile = File(...)):
    saved_path = save_upload(file)

    try:
        output_path = pdf_to_markdown(saved_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type="text/markdown", filename="converted.md")


@router.post("/scan-to-pdf")
async def scan_to_pdf_endpoint(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least 1 image.")

    saved_paths = [_save_any_upload(f) for f in files]

    try:
        output_path = scan_to_pdf(saved_paths)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="scanned.pdf")