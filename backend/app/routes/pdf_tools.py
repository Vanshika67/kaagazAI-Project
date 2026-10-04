"""
API routes for the PDF Processing module.
Each endpoint: receives file(s) + parameters -> calls the matching
service function -> returns the resulting file for download.
"""

from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.utils.file_handler import save_upload
from app.services.pdf_service.merge import merge_pdfs
from app.services.pdf_service.split import split_pdf
from app.services.pdf_service.insert_page import insert_page
from app.services.pdf_service.delete_page import delete_pages
from app.services.pdf_service.compress import compress_pdf
from app.services.pdf_service.rotate import rotate_pdf
from app.services.pdf_service.watermark import add_watermark
from app.services.pdf_service.protect import protect_pdf, unlock_pdf
from app.services.pdf_service.page_numbers import add_page_numbers
from app.services.pdf_service.remove_blank import remove_blank_pages
from app.services.pdf_service.extract_pages import extract_pages
from app.services.pdf_service.reorder_pages import reorder_pages
from app.services.pdf_service.crop import crop_pdf

router = APIRouter(prefix="/api/pdf", tags=["PDF Tools"])


@router.post("/merge")
async def merge_endpoint(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Upload at least 2 PDF files to merge.")

    saved_paths = [save_upload(f) for f in files]
    try:
        output_path = merge_pdfs(saved_paths)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="merged.pdf")


@router.post("/split")
async def split_endpoint(
    file: UploadFile = File(...),
    ranges: str = Form(None),
):
    saved_path = save_upload(file)

    parsed_ranges = None
    if ranges:
        try:
            parsed_ranges = []
            for part in ranges.split(","):
                start_str, end_str = part.split("-")
                parsed_ranges.append((int(start_str), int(end_str)))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid ranges format. Use e.g. '1-3,4-4,5-7'.",
            )

    try:
        output_path = split_pdf(saved_path, parsed_ranges)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/zip", filename="split_result.zip")


@router.post("/insert-page")
async def insert_page_endpoint(
    original_file: UploadFile = File(...),
    new_pages_file: UploadFile = File(...),
    after_page: int = Form(...),
):
    original_path = save_upload(original_file)
    new_pages_path = save_upload(new_pages_file)

    try:
        output_path = insert_page(original_path, new_pages_path, after_page)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="inserted.pdf")


@router.post("/delete-pages")
async def delete_pages_endpoint(
    file: UploadFile = File(...),
    pages: str = Form(...),
):
    saved_path = save_upload(file)

    try:
        page_list = [int(p.strip()) for p in pages.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pages format. Use e.g. '2,5,7'.")

    try:
        output_path = delete_pages(saved_path, page_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="deleted_pages.pdf")


@router.post("/compress")
async def compress_endpoint(
    file: UploadFile = File(...),
    quality: str = Form("medium"),
):
    saved_path = save_upload(file)

    try:
        output_path = compress_pdf(saved_path, quality)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")


@router.post("/rotate")
async def rotate_endpoint(
    file: UploadFile = File(...),
    angle: int = Form(...),
    pages: str = Form(None),
):
    saved_path = save_upload(file)

    page_list = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",")]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid pages format. Use e.g. '1,3,5'.")

    try:
        output_path = rotate_pdf(saved_path, angle, page_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="rotated.pdf")


@router.post("/watermark")
async def watermark_endpoint(
    file: UploadFile = File(...),
    text: str = Form("CONFIDENTIAL"),
):
    saved_path = save_upload(file)

    try:
        output_path = add_watermark(saved_path, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="watermarked.pdf")


@router.post("/protect")
async def protect_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...),
):
    saved_path = save_upload(file)

    try:
        output_path = protect_pdf(saved_path, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="protected.pdf")


@router.post("/unlock")
async def unlock_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...),
):
    saved_path = save_upload(file)

    try:
        output_path = unlock_pdf(saved_path, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="unlocked.pdf")


@router.post("/add-page-numbers")
async def page_numbers_endpoint(
    file: UploadFile = File(...),
    position: str = Form("bottom-center"),
):
    saved_path = save_upload(file)

    try:
        output_path = add_page_numbers(saved_path, position)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="numbered.pdf")


@router.post("/remove-blank-pages")
async def remove_blank_pages_endpoint(file: UploadFile = File(...)):
    saved_path = save_upload(file)

    try:
        output_path, removed_pages = remove_blank_pages(saved_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    headers = {"X-Removed-Pages": ",".join(str(p) for p in removed_pages)}
    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="no_blanks.pdf",
        headers=headers,
    )


@router.post("/extract-pages")
async def extract_pages_endpoint(
    file: UploadFile = File(...),
    pages: str = Form(...),  # e.g. "3,1,5" — order matters
):
    saved_path = save_upload(file)

    try:
        page_list = [int(p.strip()) for p in pages.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pages format. Use e.g. '3,1,5'.")

    try:
        output_path = extract_pages(saved_path, page_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="extracted.pdf")


@router.post("/reorder-pages")
async def reorder_pages_endpoint(
    file: UploadFile = File(...),
    new_order: str = Form(...),  # e.g. "3,1,2" — must include every page exactly once
):
    saved_path = save_upload(file)

    try:
        order_list = [int(p.strip()) for p in new_order.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order format. Use e.g. '3,1,2'.")

    try:
        output_path = reorder_pages(saved_path, order_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="reordered.pdf")


@router.post("/crop")
async def crop_endpoint(
    file: UploadFile = File(...),
    left: float = Form(0),
    bottom: float = Form(0),
    right: float = Form(0),
    top: float = Form(0),
):
    saved_path = save_upload(file)

    try:
        output_path = crop_pdf(saved_path, left, bottom, right, top)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="cropped.pdf")