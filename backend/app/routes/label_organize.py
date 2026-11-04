"""
label_organize.py
------------------
"Label & Organize" tool: upload several document photos (front/back of
ID cards etc.) in one go, group them, and get one PDF where each group
starts with a heading page (e.g. "AADHAAR CARD") followed by its images,
each on its own full page.
"""

import json
import os
import shutil
import uuid

import pymupdf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter()
TEMP_DIR = os.path.abspath("app/temp_files")

PAGE_WIDTH, PAGE_HEIGHT = 595, 842  # A4 in points
MARGIN = 36


def _save(upload: UploadFile) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    ext = os.path.splitext(upload.filename or "")[1] or ".jpg"
    path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


def _out(suffix: str) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


def _add_heading_page(doc: "pymupdf.Document", title: str):
    page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    rect = pymupdf.Rect(MARGIN, PAGE_HEIGHT / 2 - 40, PAGE_WIDTH - MARGIN, PAGE_HEIGHT / 2 + 40)
    page.insert_textbox(
        rect, title.upper(), fontsize=28, fontname="helv",
        align=pymupdf.TEXT_ALIGN_CENTER, color=(0.1, 0.1, 0.1),
    )
    # a thin rule under the title, just for a clean look
    y = PAGE_HEIGHT / 2 + 46
    page.draw_line((PAGE_WIDTH / 2 - 80, y), (PAGE_WIDTH / 2 + 80, y), color=(0.6, 0.6, 0.6), width=1)


def _add_image_page(doc: "pymupdf.Document", image_path: str):
    pix = pymupdf.Pixmap(image_path)
    img_w, img_h = pix.width, pix.height

    # fit the image inside the page with a margin, keeping its aspect ratio
    avail_w = PAGE_WIDTH - 2 * MARGIN
    avail_h = PAGE_HEIGHT - 2 * MARGIN
    scale = min(avail_w / img_w, avail_h / img_h)
    draw_w, draw_h = img_w * scale, img_h * scale
    x0 = (PAGE_WIDTH - draw_w) / 2
    y0 = (PAGE_HEIGHT - draw_h) / 2

    page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    rect = pymupdf.Rect(x0, y0, x0 + draw_w, y0 + draw_h)
    page.insert_image(rect, filename=image_path)


@router.post("/tools/label-organize")
async def label_organize(
    files: list[UploadFile] = File(..., description="Images in the order they should appear"),
    groups: str = Form(
        ...,
        description='JSON list, e.g. [{"label":"Aadhaar Card","count":2},{"label":"PAN Card","count":2}]',
    ),
):
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one image.")

    try:
        group_list = json.loads(groups)
        if not isinstance(group_list, list) or not group_list:
            raise ValueError
        group_list = [
            {"label": str(g["label"]).strip(), "count": int(g["count"])}
            for g in group_list
        ]
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='groups must be JSON like [{"label": "Aadhaar Card", "count": 2}].',
        )

    total_expected = sum(g["count"] for g in group_list)
    if total_expected != len(files):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Group counts add up to {total_expected}, but you uploaded "
                f"{len(files)} images. They must match."
            ),
        )
    if any(g["count"] <= 0 for g in group_list):
        raise HTTPException(status_code=400, detail="Each group's count must be at least 1.")
    if any(not g["label"] for g in group_list):
        raise HTTPException(status_code=400, detail="Every group needs a label.")

    saved_paths = [_save(f) for f in files]

    doc = pymupdf.open()
    try:
        idx = 0
        for group in group_list:
            _add_heading_page(doc, group["label"])
            for _ in range(group["count"]):
                try:
                    _add_image_page(doc, saved_paths[idx])
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Could not read image '{files[idx].filename}': {e}",
                    )
                idx += 1

        out = _out(".pdf")
        doc.save(out, garbage=4, deflate=True)
    finally:
        doc.close()

    return FileResponse(out, filename="my_documents.pdf")