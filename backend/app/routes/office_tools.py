"""
office_tools.py
----------------
1. PDF -> Word / Excel / PowerPoint
2. Protect / Unlock for ANY file (PDF, docx, xlsx, pptx, other files)
3. Generate Document (form-data version, for the frontend)
main.py adds the "/api" prefix, so paths here have no "/api".
"""

import io
import json
import os
import shutil
import uuid
import zipfile

import pymupdf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.document_generator.document_service import generate_document
from app.utils.format_wrapper import convert_pdf_to_word

router = APIRouter()
TEMP_DIR = os.path.abspath("app/temp_files")

OFFICE_EXT = (".docx", ".xlsx", ".pptx")
LEGACY_EXT = (".doc", ".xls", ".ppt")


# ------------------------------ helpers ------------------------------ #
def _save(upload: UploadFile) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    ext = os.path.splitext(upload.filename or "")[1]
    path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


def _save_pdf(upload: UploadFile) -> str:
    if not (upload.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    return _save(upload)


def _out(suffix: str) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


def _open_pdf(path: str):
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not open PDF: {e}")
    if doc.needs_pass:
        doc.close()
        raise HTTPException(status_code=400, detail="PDF is password protected. Unlock it first.")
    return doc


# ------------------------- PDF -> Word / Excel / PPT ------------------------- #
@router.post("/convert/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    src = _save_pdf(file)
    _open_pdf(src).close()
    try:
        out = convert_pdf_to_word(src)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {e}")
    return FileResponse(out, filename="converted.docx")


@router.post("/convert/pdf-to-excel")
async def pdf_to_excel(file: UploadFile = File(...)):
    import openpyxl

    src = _save_pdf(file)
    doc = _open_pdf(src)
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    found_table = False
    try:
        for page_no, page in enumerate(doc, start=1):
            for t_no, table in enumerate(page.find_tables().tables, start=1):
                ws = wb.create_sheet(f"P{page_no}_T{t_no}"[:31])
                for row in table.extract():
                    ws.append(["" if c is None else str(c) for c in row])
                found_table = True
        if not found_table:  # no tables found -> put text lines in one sheet
            ws = wb.create_sheet("Text")
            ws.append(["Page", "Text"])
            for page_no, page in enumerate(doc, start=1):
                for line in page.get_text().splitlines():
                    if line.strip():
                        ws.append([page_no, line.strip()])
    finally:
        doc.close()
    out = _out(".xlsx")
    wb.save(out)
    return FileResponse(out, filename="converted.xlsx")


@router.post("/convert/pdf-to-pptx")
async def pdf_to_pptx(file: UploadFile = File(...), dpi: int = Form(150)):
    from pptx import Presentation
    from pptx.util import Emu

    src = _save_pdf(file)
    doc = _open_pdf(src)
    prs = Presentation()
    try:
        first = True
        for page in doc:
            if first:  # slide size = first page size (1 point = 12700 EMU)
                prs.slide_width = Emu(int(page.rect.width * 12700))
                prs.slide_height = Emu(int(page.rect.height * 12700))
                first = False
            png = page.get_pixmap(dpi=dpi).tobytes("png")
            slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
            slide.shapes.add_picture(
                io.BytesIO(png), 0, 0, width=prs.slide_width, height=prs.slide_height
            )
    finally:
        doc.close()
    out = _out(".pptx")
    prs.save(out)
    return FileResponse(out, filename="converted.pptx")


# ------------------------- Protect / Unlock (any file) ------------------------- #
@router.post("/security/protect")
async def protect_any(file: UploadFile = File(...), password: str = Form(...)):
    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty.")
    name = file.filename or "file"
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    src = _save(file)

    if ext == ".pdf":
        doc = _open_pdf(src)
        out = _out(".pdf")
        try:
            doc.save(out, encryption=pymupdf.PDF_ENCRYPT_AES_256,
                     user_pw=password, owner_pw=password)
        finally:
            doc.close()
        return FileResponse(out, filename=f"{stem}_protected.pdf")

    if ext in OFFICE_EXT:
        import msoffcrypto
        out = _out(ext)
        try:
            with open(src, "rb") as f_in, open(out, "wb") as f_out:
                msoffcrypto.OfficeFile(f_in).encrypt(password, f_out)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not protect this file: {e}")
        return FileResponse(out, filename=f"{stem}_protected{ext}")

    if ext in LEGACY_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Old {ext} format is not supported. Save it as {ext}x and try again.",
        )

    # Any other file (txt, image, csv...) -> password-protected AES zip
    import pyzipper
    out = _out(".zip")
    with pyzipper.AESZipFile(out, "w", compression=pyzipper.ZIP_DEFLATED,
                             encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode())
        zf.write(src, arcname=name)
    return FileResponse(out, filename=f"{stem}_protected.zip")


@router.post("/security/unlock")
async def unlock_any(file: UploadFile = File(...), password: str = Form(...)):
    name = file.filename or "file"
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    src = _save(file)

    if ext == ".pdf":
        try:
            doc = pymupdf.open(src)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not open PDF: {e}")
        try:
            if not doc.needs_pass:
                raise HTTPException(status_code=400, detail="This PDF is not password protected.")
            if doc.authenticate(password) == 0:
                raise HTTPException(status_code=400, detail="Incorrect password.")
            out = _out(".pdf")
            doc.save(out, encryption=pymupdf.PDF_ENCRYPT_NONE)
        finally:
            doc.close()
        return FileResponse(out, filename=f"{stem}_unlocked.pdf")

    if ext in OFFICE_EXT:
        import msoffcrypto
        out = _out(ext)
        try:
            with open(src, "rb") as f_in:
                office = msoffcrypto.OfficeFile(f_in)
                if not office.is_encrypted():
                    raise HTTPException(status_code=400, detail="This file is not password protected.")
                office.load_key(password=password)
                with open(out, "wb") as f_out:
                    office.decrypt(f_out)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Incorrect password or unsupported file.")
        return FileResponse(out, filename=f"{stem}_unlocked{ext}")

    if ext == ".zip":
        import pyzipper
        try:
            with pyzipper.AESZipFile(src) as zf:
                zf.setpassword(password.encode())
                names = [n for n in zf.namelist() if not n.endswith("/")]
                data = {n: zf.read(n) for n in names}
        except RuntimeError:
            raise HTTPException(status_code=400, detail="Incorrect password.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not open zip: {e}")
        if len(data) == 1:
            n, content = next(iter(data.items()))
            out = _out(os.path.splitext(n)[1])
            with open(out, "wb") as f:
                f.write(content)
            return FileResponse(out, filename=os.path.basename(n))
        out = _out(".zip")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n, content in data.items():
                z.writestr(n, content)
        return FileResponse(out, filename=f"{stem}_unlocked.zip")

    raise HTTPException(
        status_code=400,
        detail="Unsupported file. Use PDF, DOCX, XLSX, PPTX or a protected ZIP.",
    )


# ------------------------- Generate Document (form version) ------------------------- #
@router.post("/tools/generate-document-form")
async def generate_document_form(
    template_key: str = Form(...),
    document_title: str = Form(...),
    fields: str = Form(..., description='JSON list: [{"label":"Name","value":"Test"}]'),
    output_format: str = Form("pdf"),
):
    try:
        items = json.loads(fields)
        if not isinstance(items, list):
            raise ValueError
        items = [{"label": str(i["label"]), "value": str(i["value"])} for i in items]
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='fields must be JSON like [{"label": "Name", "value": "Test"}].',
        )
    try:
        path = generate_document(template_key=template_key, document_title=document_title,
                                 fields=items, output_format=output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    ext = "docx" if output_format == "word" else "pdf"
    return FileResponse(path, filename=f"document.{ext}")