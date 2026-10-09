"""
API routes for the Page Manager tool.
"""

import json
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.utils.file_handler import save_upload
from app.services.pdf_service.page_manager import manage_pages, get_page_count

router = APIRouter(prefix="/api/pdf", tags=["Page Manager"])


@router.post("/page-info")
async def page_info_endpoint(file: UploadFile = File(...)):
    """Returns how many pages a PDF has — frontend uses this to build the plan UI."""
    saved_path = save_upload(file)
    return {"total_pages": get_page_count(saved_path)}


@router.post("/manage-pages")
async def manage_pages_endpoint(
    main_file: UploadFile = File(...),
    extra_files: Optional[List[UploadFile]] = File(None),
    plan: str = Form(...),
):
    main_path = save_upload(main_file)

    extra_paths = []
    if extra_files:
        extra_paths = [save_upload(f) for f in extra_files]

    try:
        plan_list = json.loads(plan)
    except Exception:
        raise HTTPException(status_code=400, detail="plan must be valid JSON.")

    try:
        output_path = manage_pages(main_path, extra_paths, plan_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="organized.pdf")