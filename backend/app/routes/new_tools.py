"""
new_tools.py
-------------
Extra tools:
  1. POST /convert/pdf-to-pages     - PDF -> zip of page images
  2. POST /tools/generate-document  - fill a card template, get PDF or Word
  3. POST /pdf/ocr                  - make a scanned PDF searchable
  4. POST /pdf/repair               - try to fix a damaged PDF
  5. POST /pdf/redact               - permanently remove sensitive text
  6. POST /pdf/sign                 - place a signature image on a page
  7. POST /pdf/form-fields          - list fillable form fields
  8. POST /pdf/fill-form            - fill a fillable PDF form
  9. POST /pdf/compare              - text differences between two PDFs

main.py adds the "/api" prefix, so do NOT write "/api" in the paths here.
"""

import difflib
import json
import os
import shutil
import uuid
from typing import List, Optional

import pymupdf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.convert_service.pdf_to_pages import pdf_to_pages
from app.services.document_generator.document_service import generate_document
from app.utils.format_wrapper import finalize_output

router = APIRouter()
TEMP_DIR = os.path.abspath("app/temp_files")


# ---------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------- #
def _save_upload(upload: UploadFile) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    ext = os.path.splitext(upload.filename or "")[1]
    path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


def _save_pdf_upload(upload: UploadFile) -> str:
    if not (upload.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    return _save_upload(upload)


def _out_path(suffix: str = ".pdf") -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


def _open_pdf(path: str):
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not open PDF: {e}")
    if doc.needs_pass:
        doc.close()
        raise HTTPException(status_code=400, detail="This PDF is password protected. Unlock it first.")
    return doc


def _pdf_response(pdf_path: str, output_format: str, name: str):
    """Return the PDF, or a Word file if the user asked for it."""
    final_path = finalize_output(pdf_path, output_format)
    if str(final_path).lower().endswith(".docx"):
        return FileResponse(final_path, filename=f"{name}.docx")
    return FileResponse(final_path, filename=f"{name}.pdf", media_type="application/pdf")


def _setup_tesseract():
    """Help PyMuPDF find Tesseract on Windows."""
    candidates = (
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
    )
    for base in candidates:
        tessdata = os.path.join(base, "tessdata")
        if os.path.isdir(tessdata):
            os.environ.setdefault("TESSDATA_PREFIX", tessdata)
            if base not in os.environ.get("PATH", ""):
                os.environ["PATH"] += os.pathsep + base
            return


# ---------------------------------------------------------------- #
# 1. PDF -> Pages (Images)
# ---------------------------------------------------------------- #
@router.post("/convert/pdf-to-pages")
async def pdf_to_pages_endpoint(
    file: UploadFile = File(...),
    image_format: str = Form("png"),
    dpi: int = Form(150),
):
    saved_path = _save_pdf_upload(file)
    zip_path = pdf_to_pages(saved_path, image_format=image_format, dpi=dpi)
    return FileResponse(zip_path, filename="pages.zip", media_type="application/zip")


# ---------------------------------------------------------------- #
# 2. Document / ID-Card style generator
# ---------------------------------------------------------------- #
class FieldInput(BaseModel):
    label: str
    value: str


class DocumentGenerateRequest(BaseModel):
    template_key: str            # "generic_id_card" | "marksheet"
    document_title: str
    fields: List[FieldInput]
    output_format: Optional[str] = "pdf"   # "pdf" | "word"


@router.post("/tools/generate-document")
async def generate_document_endpoint(payload: DocumentGenerateRequest):
    fields_as_dicts = [f.model_dump() for f in payload.fields]
    try:
        result_path = generate_document(
            template_key=payload.template_key,
            document_title=payload.document_title,
            fields=fields_as_dicts,
            output_format=payload.output_format,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ext = "docx" if payload.output_format == "word" else "pdf"
    return FileResponse(result_path, filename=f"document.{ext}")


# ---------------------------------------------------------------- #
# 3. OCR PDF  (needs Tesseract installed)
# ---------------------------------------------------------------- #
@router.post("/pdf/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    language: str = Form("eng"),
    dpi: int = Form(200),
    output_format: str = Form("pdf"),
):
    saved = _save_pdf_upload(file)
    _setup_tesseract()
    src = _open_pdf(saved)
    out = pymupdf.open()
    try:
        for page in src:
            pix = page.get_pixmap(dpi=dpi)
            ocr_pdf_bytes = pix.pdfocr_tobytes(language=language)
            ocr_page_doc = pymupdf.open("pdf", ocr_pdf_bytes)
            out.insert_pdf(ocr_page_doc)
            ocr_page_doc.close()
        result = _out_path()
        out.save(result, garbage=3, deflate=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"OCR failed. Is Tesseract installed (and language '{language}' available)? {e}",
        )
    finally:
        src.close()
        out.close()
    return _pdf_response(result, output_format, "ocr")


# ---------------------------------------------------------------- #
# 4. Repair PDF
# ---------------------------------------------------------------- #
@router.post("/pdf/repair")
async def repair_endpoint(
    file: UploadFile = File(...),
    output_format: str = Form("pdf"),
):
    saved = _save_pdf_upload(file)
    doc = _open_pdf(saved)   # PyMuPDF repairs minor damage while opening
    try:
        result = _out_path()
        doc.save(result, garbage=4, clean=True, deflate=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not repair this PDF: {e}")
    finally:
        doc.close()
    return _pdf_response(result, output_format, "repaired")


# ---------------------------------------------------------------- #
# 5. Redact PDF
# ---------------------------------------------------------------- #
@router.post("/pdf/redact")
async def redact_endpoint(
    file: UploadFile = File(...),
    terms: str = Form(..., description="Words/phrases to remove, one per line or comma separated"),
    output_format: str = Form("pdf"),
):
    saved = _save_pdf_upload(file)
    search_terms = [t.strip() for t in terms.replace("\n", ",").split(",") if t.strip()]
    if not search_terms:
        raise HTTPException(status_code=400, detail="Enter at least one word to redact.")

    doc = _open_pdf(saved)
    try:
        found = 0
        for page in doc:
            for term in search_terms:
                for rect in page.search_for(term):
                    page.add_redact_annot(rect, fill=(0, 0, 0))
                    found += 1
            page.apply_redactions()
        result = _out_path()
        doc.save(result, garbage=4, deflate=True)
    finally:
        doc.close()
    return _pdf_response(result, output_format, "redacted")


# ---------------------------------------------------------------- #
# 6. Sign PDF  (coordinates in points, measured from top-left)
# ---------------------------------------------------------------- #
@router.post("/pdf/sign")
async def sign_endpoint(
    file: UploadFile = File(...),
    signature: UploadFile = File(..., description="Signature image (PNG/JPG)"),
    page_number: int = Form(1),
    x: float = Form(72),
    y: float = Form(650),
    width: float = Form(150),
    height: float = Form(60),
    output_format: str = Form("pdf"),
):
    saved = _save_pdf_upload(file)
    sig_bytes = await signature.read()
    if not sig_bytes:
        raise HTTPException(status_code=400, detail="Signature image is empty.")

    doc = _open_pdf(saved)
    try:
        if page_number < 1 or page_number > len(doc):
            raise HTTPException(
                status_code=400,
                detail=f"page_number must be between 1 and {len(doc)}.",
            )
        page = doc[page_number - 1]
        rect = pymupdf.Rect(x, y, x + width, y + height)
        try:
            page.insert_image(rect, stream=sig_bytes)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid signature image: {e}")
        result = _out_path()
        doc.save(result, garbage=3, deflate=True)
    finally:
        doc.close()
    return _pdf_response(result, output_format, "signed")


# ---------------------------------------------------------------- #
# 7. List form fields
# ---------------------------------------------------------------- #
@router.post("/pdf/form-fields")
async def form_fields_endpoint(file: UploadFile = File(...)):
    saved = _save_pdf_upload(file)
    doc = _open_pdf(saved)
    fields = []
    try:
        for page_index, page in enumerate(doc, start=1):
            for w in page.widgets() or []:
                fields.append({
                    "name": w.field_name,
                    "type": w.field_type_string,
                    "value": w.field_value,
                    "page": page_index,
                })
    finally:
        doc.close()
    return {"total_fields": len(fields), "fields": fields}


# ---------------------------------------------------------------- #
# 8. Fill PDF form   (fields = JSON like {"Name": "Vanshika", "Agree": true})
# ---------------------------------------------------------------- #
@router.post("/pdf/fill-form")
async def fill_form_endpoint(
    file: UploadFile = File(...),
    fields: str = Form(..., description='JSON object, e.g. {"Name": "Vanshika"}'),
    output_format: str = Form("pdf"),
):
    saved = _save_pdf_upload(file)
    try:
        values = json.loads(fields)
        if not isinstance(values, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail='fields must be a JSON object like {"Name": "Vanshika"}.')

    doc = _open_pdf(saved)
    try:
        filled = 0
        for page in doc:
            for w in page.widgets() or []:
                if w.field_name not in values:
                    continue
                val = values[w.field_name]
                if w.field_type == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                    is_on = str(val).strip().lower() in ("true", "yes", "on", "1")
                    w.field_value = w.on_state() if is_on else "Off"
                else:
                    w.field_value = str(val)
                w.update()
                filled += 1
        if filled == 0:
            raise HTTPException(
                status_code=400,
                detail="No matching form fields found. Use /pdf/form-fields to get the exact field names.",
            )
        result = _out_path()
        doc.save(result, garbage=3, deflate=True)
    finally:
        doc.close()
    return _pdf_response(result, output_format, "filled")


# ---------------------------------------------------------------- #
# 9. Compare PDFs (text differences)
# ---------------------------------------------------------------- #
def _pdf_lines(path: str) -> List[str]:
    doc = _open_pdf(path)
    lines = []
    try:
        for page_index, page in enumerate(doc, start=1):
            for line in page.get_text().splitlines():
                if line.strip():
                    lines.append(line.strip())
    finally:
        doc.close()
    return lines


@router.post("/pdf/compare")
async def compare_endpoint(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    path1 = _save_pdf_upload(file1)
    path2 = _save_pdf_upload(file2)
    lines1 = _pdf_lines(path1)
    lines2 = _pdf_lines(path2)

    diff = list(difflib.unified_diff(
        lines1, lines2, fromfile=file1.filename, tofile=file2.filename, lineterm="", n=0
    ))
    changes = [d for d in diff if d[:1] in ("+", "-") and not d.startswith(("+++", "---"))]
    similarity = difflib.SequenceMatcher(None, lines1, lines2).ratio()

    return {
        "identical": len(changes) == 0,
        "similarity_percent": round(similarity * 100, 1),
        "total_changes": len(changes),
        "differences": changes[:300],   # "-" only in file 1, "+" only in file 2
    }