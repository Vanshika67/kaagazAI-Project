import io
import uuid

import anthropic
import pymupdf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image
from pydantic import BaseModel

router = APIRouter(prefix="/api")

MODEL = "claude-sonnet-5-5"
_client = None


def get_client():
    """Client tabhi banta hai jab AI tool use hota hai (key na ho to baaki backend chalta rahe)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # ANTHROPIC_API_KEY env/.env se leta hai
    return _client


# ======================= helpers =======================
def open_pdf(data: bytes):
    try:
        return pymupdf.open(stream=data, filetype="pdf")
    except Exception as e:
        raise HTTPException(400, f"Invalid PDF: {e}")


def pdf_response(data: bytes, name: str, extra_headers: dict | None = None):
    headers = {
        "Content-Disposition": f'attachment; filename="{name}"',
        "Access-Control-Expose-Headers": "Content-Disposition, X-Final-Size-KB, X-Target-Reached",
    }
    if extra_headers:
        headers.update(extra_headers)
    return Response(content=data, media_type="application/pdf", headers=headers)


def rasterize(doc, dpi=150, gray=False):
    """Har page ko image bana kar naya PDF banata hai."""
    out = pymupdf.open()
    for page in doc:
        pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY if gray else pymupdf.csRGB)
        new_page = out.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, pixmap=pix)
    return out


# ======================= 1. PDF to Text =======================
@router.post("/pdf-to-text")
async def pdf_to_text(file: UploadFile = File(...)):
    doc = open_pdf(await file.read())
    parts = [f"--- Page {i + 1} ---\n{page.get_text()}" for i, page in enumerate(doc)]
    doc.close()
    return Response(
        content="\n\n".join(parts).encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="output.txt"'},
    )


# ======================= 2. Edit Metadata =======================
@router.post("/edit-metadata")
async def edit_metadata(
    file: UploadFile = File(...),
    title: str = Form(""),
    author: str = Form(""),
    subject: str = Form(""),
    keywords: str = Form(""),
):
    doc = open_pdf(await file.read())
    meta = doc.metadata or {}
    meta.update({"title": title, "author": author, "subject": subject, "keywords": keywords})
    doc.set_metadata(meta)
    data = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return pdf_response(data, "metadata-updated.pdf")


# ======================= 3. Compress to Target Size =======================
@router.post("/compress-target")
async def compress_target(file: UploadFile = File(...), target_kb: int = Form(200)):
    raw = await file.read()
    target = target_kb * 1024
    levels = [(150, 75), (110, 60), (90, 45), (72, 30), (60, 20)]  # (dpi, jpeg quality) high -> low

    best = None
    for dpi, quality in levels:
        doc = open_pdf(raw)
        try:
            doc.rewrite_images(dpi_threshold=dpi + 20, dpi_target=dpi, quality=quality)
        except Exception:
            pass  # purana PyMuPDF: sirf structure compress hoga
        data = doc.tobytes(garbage=4, deflate=True, clean=True)
        doc.close()
        if best is None or len(data) < len(best):
            best = data
        if len(data) <= target:
            break

    if len(best) >= len(raw):  # compress karke bada ho gaya to original do
        best = raw

    return pdf_response(
        best,
        "compressed.pdf",
        {
            "X-Final-Size-KB": str(round(len(best) / 1024, 1)),
            "X-Target-Reached": str(len(best) <= target).lower(),
        },
    )


# ======================= 4. Add Header / Footer =======================
@router.post("/header-footer")
async def header_footer(
    file: UploadFile = File(...),
    header: str = Form(""),
    footer: str = Form(""),
    fontsize: int = Form(10),
):
    doc = open_pdf(await file.read())
    for page in doc:
        r = page.rect
        if header:
            page.insert_textbox(
                pymupdf.Rect(36, 14, r.width - 36, 14 + fontsize * 2.5),
                header, fontsize=fontsize, fontname="helv", align=1,
            )
        if footer:
            page.insert_textbox(
                pymupdf.Rect(36, r.height - fontsize * 2.5 - 14, r.width - 36, r.height - 14),
                footer, fontsize=fontsize, fontname="helv", align=1,
            )
    data = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return pdf_response(data, "header-footer.pdf")


# ======================= 5. Grayscale PDF =======================
@router.post("/grayscale")
async def grayscale(file: UploadFile = File(...), dpi: int = Form(150)):
    doc = open_pdf(await file.read())
    out = rasterize(doc, dpi=dpi, gray=True)
    data = out.tobytes(garbage=4, deflate=True)
    doc.close()
    out.close()
    return pdf_response(data, "grayscale.pdf")


# ======================= 6. Flatten PDF =======================
@router.post("/flatten")
async def flatten(file: UploadFile = File(...)):
    doc = open_pdf(await file.read())
    try:
        doc.bake(annots=True, widgets=True)  # form fields + annotations permanent
        data = doc.tobytes(garbage=3, deflate=True)
        doc.close()
    except Exception:  # purana PyMuPDF: fallback
        out = rasterize(doc, dpi=150)
        data = out.tobytes(garbage=3, deflate=True)
        doc.close()
        out.close()
    return pdf_response(data, "flattened.pdf")


# ======================= 7. Photo Resizer (exact KB) =======================
@router.post("/photo-resize")
async def photo_resize(
    file: UploadFile = File(...),
    target_kb: int = Form(50),
    width: int = Form(0),
    height: int = Form(0),
):
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image")

    if width > 0 and height > 0:
        img = img.resize((width, height), Image.LANCZOS)

    target = target_kb * 1024

    def encode(im, q):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True)
        return buf.getvalue()

    data = None
    for _ in range(8):  # quality kam karo, phir size kam karo
        lo, hi, best = 5, 95, None
        while lo <= hi:  # binary search on quality
            mid = (lo + hi) // 2
            d = encode(img, mid)
            if len(d) <= target:
                best, lo = d, mid + 1
            else:
                hi = mid - 1
        if best:
            data = best
            break
        img = img.resize((int(img.width * 0.85), int(img.height * 0.85)), Image.LANCZOS)

    if not data:
        raise HTTPException(400, "Target size bahut chhota hai")
    return Response(
        content=data,
        media_type="image/jpeg",
        headers={"Content-Disposition": 'attachment; filename="resized.jpg"'},
    )


# ======================= 8. Chat with PDF (Claude API) =======================
DOCS: dict[str, str] = {}  # doc_id -> text (memory mein; server restart par chali jaati hai)
MAX_CHARS = 150_000


@router.post("/chat-pdf/upload")
def chat_upload(file: UploadFile = File(...)):
    doc = open_pdf(file.file.read())
    text = "\n\n".join(f"[Page {i + 1}]\n{p.get_text()}" for i, p in enumerate(doc))
    doc.close()
    if not text.strip():
        raise HTTPException(400, "Is PDF mein text nahi mila (scanned hai to pehle OCR PDF use karein)")
    doc_id = uuid.uuid4().hex
    DOCS[doc_id] = text[:MAX_CHARS]
    return {"doc_id": doc_id, "chars": len(text), "truncated": len(text) > MAX_CHARS}


class Msg(BaseModel):
    role: str  # "user" ya "assistant"
    content: str


class AskBody(BaseModel):
    doc_id: str
    question: str
    history: list[Msg] = []


@router.post("/chat-pdf/ask")
def chat_ask(body: AskBody):
    text = DOCS.get(body.doc_id)
    if not text:
        raise HTTPException(404, "Document expire ho gaya, dobara upload karein")

    system = (
        "You answer questions about the document below. Use only the document. "
        "If the answer is not in it, say so. Mention page numbers when helpful. "
        "Reply in the same language as the user's question.\n\n<document>\n" + text + "\n</document>"
    )
    messages = [m.model_dump() for m in body.history[-10:]]
    messages.append({"role": "user", "content": body.question})

    try:
        res = get_client().messages.create(
            model=MODEL, max_tokens=1000, system=system, messages=messages,
        )
    except Exception as e:
        raise HTTPException(502, f"AI error: {e}")
    return {"answer": res.content[0].text}