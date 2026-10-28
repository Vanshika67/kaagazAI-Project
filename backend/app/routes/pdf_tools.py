"""
API routes for the PDF Processing module.
Each endpoint: receives file(s) + parameters -> calls the matching
service function -> returns the resulting file for download.
"""

from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.utils.file_handler import save_upload
from app.utils.format_wrapper import normalize_to_pdf, normalize_many_to_pdf, finalize_output
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
from app.services.pdf_service.edit import add_text_to_pdf


router = APIRouter(prefix="/api/pdf", tags=["PDF Tools"])


def _output_filename(base_name: str, output_format: str) -> str:
    ext = "docx" if output_format == "word" else "pdf"
    return f"{base_name}.{ext}"


def _output_media_type(output_format: str) -> str:
    if output_format == "word":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "application/pdf"


@router.post("/merge")
async def merge_endpoint(
    files: List[UploadFile] = File(...),
    output_format: str = Form("pdf"),
):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Upload at least 2 PDF files to merge.")

    try:
        saved_paths = [save_upload(f) for f in files]
        normalized_paths = normalize_many_to_pdf(saved_paths)
        output_path = merge_pdfs(normalized_paths)
        output_path = finalize_output(output_path, output_format)
    except Exception as e:
        import traceback
        error_text = traceback.format_exc()
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(error_text)
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("merged", output_format),
    )

@router.post("/split")
async def split_endpoint(
    file: UploadFile = File(...),
    ranges: str = Form(None),
):
    # NOTE: split returns a ZIP of multiple PDFs, so word output isn't offered here.
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

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
    output_format: str = Form("pdf"),
):
    original_path = save_upload(original_file)
    new_pages_path = save_upload(new_pages_file)

    original_path = normalize_to_pdf(original_path)
    new_pages_path = normalize_to_pdf(new_pages_path)

    try:
        output_path = insert_page(original_path, new_pages_path, after_page)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("inserted", output_format),
    )


@router.post("/delete-pages")
async def delete_pages_endpoint(
    file: UploadFile = File(...),
    pages: str = Form(...),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        page_list = [int(p.strip()) for p in pages.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pages format. Use e.g. '2,5,7'.")

    try:
        output_path = delete_pages(saved_path, page_list)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("deleted_pages", output_format),
    )


@router.post("/compress")
async def compress_endpoint(
    file: UploadFile = File(...),
    quality: str = Form("medium"),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path = compress_pdf(saved_path, quality)
        output_path = finalize_output(output_path, output_format)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("compressed", output_format),
    )


@router.post("/rotate")
async def rotate_endpoint(
    file: UploadFile = File(...),
    angle: int = Form(...),
    pages: str = Form(None),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    page_list = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",")]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid pages format. Use e.g. '1,3,5'.")

    try:
        output_path = rotate_pdf(saved_path, angle, page_list)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("rotated", output_format),
    )


@router.post("/watermark")
async def watermark_endpoint(
    file: UploadFile = File(...),
    text: str = Form("CONFIDENTIAL"),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path = add_watermark(saved_path, text)
        output_path = finalize_output(output_path, output_format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("watermarked", output_format),
    )


@router.post("/protect")
async def protect_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...),
):
    # NOTE: no output_format here on purpose — a password-protected file
    # must stay PDF; Word format has no equivalent "protect" meaning here.
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path = protect_pdf(saved_path, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="protected.pdf")


@router.post("/unlock")
async def unlock_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    # no normalize_to_pdf here — an encrypted PDF should be uploaded as PDF, not Word

    try:
        output_path = unlock_pdf(saved_path, password)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("unlocked", output_format),
    )


@router.post("/add-page-numbers")
async def page_numbers_endpoint(
    file: UploadFile = File(...),
    position: str = Form("bottom-center"),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path = add_page_numbers(saved_path, position)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("numbered", output_format),
    )


@router.post("/remove-blank-pages")
async def remove_blank_pages_endpoint(
    file: UploadFile = File(...),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path, removed_pages = remove_blank_pages(saved_path)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    headers = {"X-Removed-Pages": ",".join(str(p) for p in removed_pages)}
    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("no_blanks", output_format),
        headers=headers,
    )


@router.post("/extract-pages")
async def extract_pages_endpoint(
    file: UploadFile = File(...),
    pages: str = Form(...),  # e.g. "3,1,5" — order matters
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        page_list = [int(p.strip()) for p in pages.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pages format. Use e.g. '3,1,5'.")

    try:
        output_path = extract_pages(saved_path, page_list)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("extracted", output_format),
    )


@router.post("/reorder-pages")
async def reorder_pages_endpoint(
    file: UploadFile = File(...),
    new_order: str = Form(...),  # e.g. "3,1,2" — must include every page exactly once
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        order_list = [int(p.strip()) for p in new_order.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order format. Use e.g. '3,1,2'.")

    try:
        output_path = reorder_pages(saved_path, order_list)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("reordered", output_format),
    )


@router.post("/crop")
async def crop_endpoint(
    file: UploadFile = File(...),
    left: float = Form(0),
    bottom: float = Form(0),
    right: float = Form(0),
    top: float = Form(0),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path = crop_pdf(saved_path, left, bottom, right, top)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("cropped", output_format),
    )


@router.post("/edit-add-text")
async def edit_add_text_endpoint(
    file: UploadFile = File(...),
    page_number: int = Form(...),
    text: str = Form(...),
    x: float = Form(...),
    y: float = Form(...),
    font_size: float = Form(12),
    output_format: str = Form("pdf"),
):
    saved_path = save_upload(file)
    saved_path = normalize_to_pdf(saved_path)

    try:
        output_path = add_text_to_pdf(saved_path, page_number, text, x, y, font_size)
        output_path = finalize_output(output_path, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        output_path,
        media_type=_output_media_type(output_format),
        filename=_output_filename("edited", output_format),
    )