import io, os, re, csv, json, math, shutil, socket, zipfile, tempfile, ipaddress, subprocess
from urllib.parse import urlparse
import pymupdf
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
import anthropic

router = APIRouter(prefix="/api")
MODEL = "claude-sonnet-5-5"

_ai = None


def get_ai():
    """Client tabhi banta hai jab AI tool use hota hai (key na ho to baaki backend chalta rahe)."""
    global _ai
    if _ai is None:
        _ai = anthropic.Anthropic()  # ANTHROPIC_API_KEY env / .env se leta hai
    return _ai


# ======================= helpers =======================
def out(data, name, mime="application/pdf"):
    return Response(content=data, media_type=mime, headers={
        "Content-Disposition": f'attachment; filename="{name}"',
        "Access-Control-Expose-Headers": "Content-Disposition"})

def open_pdf(raw: bytes):
    try:
        return pymupdf.open(stream=raw, filetype="pdf")
    except Exception as e:
        raise HTTPException(400, f"Invalid PDF: {e}")

def make_zip(items):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    return buf.getvalue()

def pdf_range(src, s, e):
    d = pymupdf.open()
    d.insert_pdf(src, from_page=s, to_page=e)
    b = d.tobytes(garbage=3, deflate=True)
    d.close()
    return b

def pdf_text(raw: bytes, limit=150_000):
    doc = open_pdf(raw)
    t = "\n\n".join(f"[Page {i+1}]\n{p.get_text()}" for i, p in enumerate(doc))
    doc.close()
    if not t.strip():
        raise HTTPException(400, "PDF mein text nahi mila (scanned hai to Hindi/OCR tool use karein)")
    return t[:limit]

def ask_claude(system, prompt, max_tokens=2000):
    try:
        r = get_ai().messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                     messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    except Exception as e:
        raise HTTPException(502, f"AI error: {e}")


# ======================= ORGANIZE / EDIT =======================
@router.post("/highlight")
async def highlight(file: UploadFile = File(...), text: str = Form(...)):
    doc = open_pdf(await file.read())
    words = [w.strip() for w in text.split(",") if w.strip()]
    n = 0
    for page in doc:
        for w in words:
            for q in page.search_for(w, quads=True):
                page.add_highlight_annot(q)
                n += 1
    if n == 0:
        raise HTTPException(404, "Ye text PDF mein nahi mila")
    data = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return out(data, "highlighted.pdf")


@router.post("/split-size")
async def split_size(file: UploadFile = File(...), max_mb: float = Form(1.0)):
    src = open_pdf(await file.read())
    limit, n, start, items = int(max_mb * 1024 * 1024), len(src), 0, []
    while start < n:
        end = start
        while end < n:
            size = len(pdf_range(src, start, end))
            if size > limit and end > start:
                break
            end += 1
        items.append((f"part_{len(items)+1}.pdf", pdf_range(src, start, end - 1)))
        start = end
    src.close()
    return out(make_zip(items), "split-by-size.zip", "application/zip")


@router.post("/split-smart")
async def split_smart(file: UploadFile = File(...), mode: str = Form("blank")):
    src = open_pdf(await file.read())
    n, ranges = len(src), []
    if mode == "blank":
        cur = []
        for i, p in enumerate(src):
            blank = not p.get_text().strip() and not p.get_images() and not p.get_drawings()
            if blank:
                if cur:
                    ranges.append((cur[0], cur[-1])); cur = []
            else:
                cur.append(i)
        if cur:
            ranges.append((cur[0], cur[-1]))
    else:  # bookmarks
        starts = sorted({t[2] - 1 for t in src.get_toc() if t[0] == 1})
        if not starts:
            raise HTTPException(400, "Is PDF mein bookmarks nahi hain")
        if starts[0] > 0:
            starts.insert(0, 0)
        ranges = [(s, e - 1) for s, e in zip(starts, starts[1:] + [n])]
    if not ranges:
        raise HTTPException(400, "Split karne layak kuch nahi mila")
    items = [(f"part_{i+1}.pdf", pdf_range(src, s, e)) for i, (s, e) in enumerate(ranges)]
    src.close()
    return out(make_zip(items), "split.zip", "application/zip")


@router.post("/nup")
async def nup(file: UploadFile = File(...), per_sheet: int = Form(4), mode: str = Form("nup")):
    src = open_pdf(await file.read())
    total_pages = len(src)
    if mode == "booklet":   # saddle-stitch: 2-up landscape, duplex print
        total = math.ceil(total_pages / 4) * 4
        pairs = []
        for k in range(total // 4):
            pairs.append((total - 1 - 2 * k, 2 * k))
            pairs.append((2 * k + 1, total - 2 - 2 * k))
        W, H, cols, rows = 842, 595, 2, 1
    else:
        per_sheet = 2 if per_sheet == 2 else 4
        W, H, cols, rows = (842, 595, 2, 1) if per_sheet == 2 else (595, 842, 2, 2)
        pairs = [tuple(range(i, i + per_sheet)) for i in range(0, total_pages, per_sheet)]

    res = pymupdf.open()
    cw, ch = W / cols, H / rows
    for group in pairs:
        page = res.new_page(width=W, height=H)
        for j, pno in enumerate(group):
            if pno >= total_pages:
                continue
            r, c = divmod(j, cols)
            page.show_pdf_page(pymupdf.Rect(c*cw+8, r*ch+8, (c+1)*cw-8, (r+1)*ch-8), src, pno)
    data = res.tobytes(garbage=3, deflate=True)
    src.close(); res.close()
    return out(data, "booklet.pdf" if mode == "booklet" else "n-up.pdf")


SIZES = {"A3": (842, 1191), "A4": (595, 842), "A5": (420, 595), "Letter": (612, 792), "Legal": (612, 1008)}

@router.post("/resize-page")
async def resize_page(file: UploadFile = File(...), size: str = Form("A4")):
    if size not in SIZES:
        raise HTTPException(400, "Unknown size")
    src = open_pdf(await file.read())
    res = pymupdf.open()
    for page in src:
        w, h = SIZES[size]
        if page.rect.width > page.rect.height:
            w, h = h, w
        np_ = res.new_page(width=w, height=h)
        np_.show_pdf_page(np_.rect, src, page.number)   # aspect ratio preserve hota hai
    data = res.tobytes(garbage=3, deflate=True)
    src.close(); res.close()
    return out(data, f"resized-{size}.pdf")


# ======================= CONVERT =======================
@router.post("/pdf-to-csv")
async def pdf_to_csv(file: UploadFile = File(...)):
    doc = open_pdf(await file.read())
    buf, found = io.StringIO(), False
    w = csv.writer(buf)
    for i, page in enumerate(doc):
        for t in page.find_tables().tables:
            found = True
            w.writerow([f"# Page {i+1}"])
            for row in t.extract():
                w.writerow([c or "" for c in row])
            w.writerow([])
    doc.close()
    if not found:
        raise HTTPException(404, "Koi table nahi mila")
    return out(buf.getvalue().encode("utf-8-sig"), "tables.csv", "text/csv")


@router.post("/pdf-to-pdfa")
async def pdf_to_pdfa(file: UploadFile = File(...)):
    exe = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")
    if not exe:
        raise HTTPException(500, "Ghostscript install nahi hai")
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, "in.pdf"), os.path.join(tmp, "out.pdf")
        with open(src, "wb") as f:
            f.write(await file.read())
        try:
            subprocess.run([exe, "-dPDFA=2", "-dPDFACompatibilityPolicy=1", "-dBATCH", "-dNOPAUSE",
                            "-dQUIET", "-sColorConversionStrategy=RGB", "-sDEVICE=pdfwrite",
                            f"-sOutputFile={dst}", src], check=True)
        except subprocess.CalledProcessError:
            raise HTTPException(500, "PDF/A conversion fail hua")
        with open(dst, "rb") as f:
            return out(f.read(), "pdfa.pdf")


@router.post("/markdown-to-pdf")
async def markdown_to_pdf(text: str = Form(""), file: UploadFile | None = File(None)):
    import markdown
    from xhtml2pdf import pisa
    if file is not None and file.filename:
        text = (await file.read()).decode("utf-8", errors="ignore")
    if not text.strip():
        raise HTTPException(400, "Markdown text khali hai")
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    css = "<style>body{font-family:Helvetica;font-size:11pt}code,pre{background:#eee}table,td,th{border:1px solid #999;border-collapse:collapse;padding:4px}</style>"
    buf = io.BytesIO()
    pisa.CreatePDF(css + html, dest=buf)
    return out(buf.getvalue(), "markdown.pdf")


@router.post("/table-to-pdf")
async def table_to_pdf(file: UploadFile = File(...)):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    raw = (await file.read()).decode("utf-8-sig", errors="ignore")
    try:
        if file.filename.lower().endswith(".json"):
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            keys = list(dict.fromkeys(k for r in data for k in r))
            rows = [keys] + [[str(r.get(k, "")) for k in keys] for r in data]
        else:
            rows = list(csv.reader(io.StringIO(raw)))
    except Exception as e:
        raise HTTPException(400, f"File parse nahi hui: {e}")
    if not rows:
        raise HTTPException(400, "File khali hai")
    buf = io.BytesIO()
    size = landscape(A4) if len(rows[0]) > 6 else A4
    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                           ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                           ("FONTSIZE", (0, 0), (-1, -1), 8),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")])]))
    SimpleDocTemplate(buf, pagesize=size).build([t])
    return out(buf.getvalue(), "table.pdf")


def check_url(url: str):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise HTTPException(400, "Valid http/https URL daalein")
    try:
        for info in socket.getaddrinfo(p.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise HTTPException(400, "Ye URL allowed nahi hai")
    except socket.gaierror:
        raise HTTPException(400, "Website nahi mili")

@router.post("/url-to-pdf")
async def url_to_pdf(url: str = Form(...)):
    check_url(url)     # SSRF se bachne ke liye (localhost / private IP block)
    try:
        from weasyprint import HTML
        data = HTML(url=url).write_pdf()
    except Exception as e:
        raise HTTPException(500, f"Page convert nahi hua: {e}")
    return out(data, "webpage.pdf")


@router.post("/qr-pdf")
async def qr_pdf(file: UploadFile = File(...), text: str = Form(...), position: str = Form("br"),
                 size: int = Form(80), pages: str = Form("all")):
    import qrcode
    doc = open_pdf(await file.read())
    b = io.BytesIO()
    qrcode.make(text).save(b, "PNG")
    png = b.getvalue()
    for i, page in enumerate(doc):
        if pages == "first" and i > 0:
            break
        r, m = page.rect, 20
        x = r.width - size - m if "r" in position else m
        y = r.height - size - m if "b" in position else m
        page.insert_image(pymupdf.Rect(x, y, x + size, y + size), stream=png)
    data = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return out(data, "with-qr.pdf")


# ======================= SECURITY =======================
@router.post("/remove-metadata")
async def remove_metadata(file: UploadFile = File(...)):
    doc = open_pdf(await file.read())
    doc.set_metadata({})
    doc.del_xml_metadata()
    data = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return out(data, "clean.pdf")


@router.post("/digital-sign")
async def digital_sign(file: UploadFile = File(...), cert: UploadFile = File(...),
                       password: str = Form("")):
    from pyhanko.sign import signers
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    pdf = await file.read()
    with tempfile.TemporaryDirectory() as tmp:
        p12 = os.path.join(tmp, "cert.p12")
        with open(p12, "wb") as f:
            f.write(await cert.read())
        try:
            signer = signers.SimpleSigner.load_pkcs12(
                pfx_file=p12, passphrase=password.encode() if password else None)
            w = IncrementalPdfFileWriter(io.BytesIO(pdf))
            res = signers.sign_pdf(w, signers.PdfSignatureMetadata(field_name="Signature1"), signer=signer)
        except Exception as e:
            raise HTTPException(400, f"Signing fail: certificate/password check karein ({e})")
        return out(res.getvalue(), "signed.pdf")


PATTERNS = {
    "email":   r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "phone":   r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}",
    "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "pan":     r"\b[A-Z]{5}\d{4}[A-Z]\b",
}

@router.post("/auto-redact")
async def auto_redact(file: UploadFile = File(...), types: str = Form("email,phone,aadhaar,pan")):
    doc = open_pdf(await file.read())
    chosen = [t.strip() for t in types.split(",") if t.strip() in PATTERNS]
    count = 0
    for page in doc:
        txt = page.get_text()
        for key in chosen:
            for m in set(re.findall(PATTERNS[key], txt)):
                for rect in page.search_for(m):
                    page.add_redact_annot(rect, fill=(0, 0, 0)); count += 1
        page.apply_redactions()
    if count == 0:
        raise HTTPException(404, "Koi sensitive data nahi mila")
    data = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return out(data, "redacted.pdf")


@router.post("/aadhaar-mask")
async def aadhaar_mask(file: UploadFile = File(...)):
    doc = open_pdf(await file.read())
    count = 0
    for page in doc:
        for m in set(re.findall(PATTERNS["aadhaar"], page.get_text())):
            cnt, idx = 0, 0
            for k, ch in enumerate(m):         # pehle 8 digits tak
                if ch.isdigit():
                    cnt += 1
                    if cnt == 8:
                        idx = k + 1; break
            for rect in page.search_for(m[:idx]):
                page.add_redact_annot(rect, fill=(0, 0, 0)); count += 1
        page.apply_redactions()
    if count == 0:
        raise HTTPException(404, "Aadhaar number nahi mila (scanned image ho to text layer nahi hoti)")
    data = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return out(data, "aadhaar-masked.pdf")


# ======================= PRODUCTIVITY =======================
def read_img(raw):
    try:
        im = Image.open(io.BytesIO(raw))
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, "white")
            im = im.convert("RGBA"); bg.paste(im, mask=im.split()[3]); return bg
        return im.convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image")

@router.post("/passport-photo")
async def passport_photo(file: UploadFile = File(...), sheet: str = Form("no")):
    im = read_img(await file.read())
    W, H = 413, 531                              # 35x45 mm @ 300 dpi
    target = W / H
    if im.width / im.height > target:            # bahut wide: sides crop
        nw = int(im.height * target); l = (im.width - nw) // 2
        im = im.crop((l, 0, l + nw, im.height))
    else:                                        # bahut tall: neeche se crop (chehra upar hota hai)
        nh = int(im.width / target); t = int((im.height - nh) * 0.2)
        im = im.crop((0, t, im.width, t + nh))
    im = im.resize((W, H), Image.LANCZOS)
    buf = io.BytesIO()
    if sheet == "yes":                           # 4x6 inch sheet, 6 copies
        canvas = Image.new("RGB", (1200, 1800), "white")
        for r in range(3):
            for c in range(2):
                canvas.paste(im, (120 + c * (W + 40), 60 + r * (H + 40)))
        canvas.save(buf, "JPEG", quality=95, dpi=(300, 300))
        return out(buf.getvalue(), "passport-sheet.jpg", "image/jpeg")
    im.save(buf, "JPEG", quality=95, dpi=(300, 300))
    return out(buf.getvalue(), "passport-photo.jpg", "image/jpeg")


@router.post("/image-compress")
async def image_compress(file: UploadFile = File(...), quality: int = Form(70), max_width: int = Form(0)):
    im = read_img(await file.read())
    if max_width and im.width > max_width:
        im = im.resize((max_width, int(im.height * max_width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=max(5, min(95, quality)), optimize=True)
    return out(buf.getvalue(), "compressed.jpg", "image/jpeg")


@router.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    from rembg import remove
    try:
        data = remove(await file.read())
    except Exception as e:
        raise HTTPException(500, f"Background remove fail: {e}")
    return out(data, "no-background.png", "image/png")


@router.post("/invoice")
async def invoice(seller: str = Form(...), buyer: str = Form(...), invoice_no: str = Form("INV-001"),
                  items: str = Form(...), gst: float = Form(18)):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    rows, sub = [["Item", "Qty", "Rate", "Amount"]], 0.0
    for line in items.strip().splitlines():       # format: Item, Qty, Rate
        try:
            name, qty, rate = [x.strip() for x in line.split(",")]
            amt = float(qty) * float(rate); sub += amt
            rows.append([name, qty, f"{float(rate):.2f}", f"{amt:.2f}"])
        except ValueError:
            raise HTTPException(400, f"Line galat hai: '{line}'. Format: Item, Qty, Rate")
    tax = sub * gst / 100
    rows += [["", "", "Subtotal", f"{sub:.2f}"], ["", "", f"GST {gst:g}%", f"{tax:.2f}"],
             ["", "", "TOTAL (Rs.)", f"{sub + tax:.2f}"]]
    s = getSampleStyleSheet()
    t = Table(rows, colWidths=[260, 50, 80, 90])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                           ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -4), 0.4, colors.grey),
                           ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                           ("ALIGN", (1, 0), (-1, -1), "RIGHT")]))
    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4).build([
        Paragraph("INVOICE", s["Title"]), Paragraph(f"Invoice No: {invoice_no}", s["Normal"]),
        Spacer(1, 12), Paragraph(f"<b>From:</b> {seller}", s["Normal"]),
        Paragraph(f"<b>Bill To:</b> {buyer}", s["Normal"]), Spacer(1, 16), t])
    return out(buf.getvalue(), f"{invoice_no}.pdf")


# ======================= AI FEATURES =======================
@router.post("/ai-summarize")
async def ai_summarize(file: UploadFile = File(...), length: str = Form("medium"),
                       language: str = Form("English")):
    text = pdf_text(await file.read())
    style = {"short": "in 3-4 sentences", "medium": "in one clear paragraph plus 5 bullet points",
             "detailed": "section by section with key points and numbers"}.get(length, "briefly")
    ans = ask_claude("You summarize documents accurately. Use only the document.",
                     f"Summarize this document {style}. Write the summary in {language}.\n\n<document>\n{text}\n</document>")
    return out(ans.encode("utf-8"), "summary.txt", "text/plain; charset=utf-8")


@router.post("/ai-translate")
async def ai_translate(file: UploadFile = File(...), target: str = Form("Hindi")):
    text = pdf_text(await file.read(), limit=30_000)
    chunks = [text[i:i + 6000] for i in range(0, len(text), 6000)]
    parts = [ask_claude(f"Translate the user's text to {target}. Keep the structure and [Page N] markers. "
                        "Output only the translation.", c, max_tokens=4000) for c in chunks]
    return out("\n\n".join(parts).encode("utf-8"), f"translated-{target}.txt", "text/plain; charset=utf-8")


@router.post("/ai-extract")
async def ai_extract(file: UploadFile = File(...), doc_type: str = Form("invoice"), fmt: str = Form("json")):
    text = pdf_text(await file.read(), limit=60_000)
    fields = {"invoice": "invoice_number, date, seller, buyer, gst_number, items (list of {name, qty, rate, amount}), subtotal, tax, total",
              "resume": "name, email, phone, location, summary, skills (list), experience (list of {company, role, duration, details}), education (list of {institute, degree, year})"
              }.get(doc_type, "all key fields you can find, as sensible keys")
    raw = ask_claude("You extract structured data. Reply with ONLY valid JSON, no markdown, no comments. "
                     "Use null for missing values.", f"Extract: {fields}\n\n<document>\n{text}\n</document>", 3000)
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(502, "AI ne valid JSON nahi diya, dobara try karein")
    if fmt == "json":
        return out(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"), "data.json", "application/json")
    from openpyxl import Workbook
    if isinstance(data, list):
        data = {"items": data}
    wb = Workbook(); ws = wb.active; ws.title = "Details"
    for k, v in data.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            sh = wb.create_sheet(str(k)[:30])
            cols = list(dict.fromkeys(c for r in v for c in r))
            sh.append(cols)
            for r in v:
                sh.append([str(r.get(c, "")) if isinstance(r.get(c), (list, dict)) else r.get(c) for c in cols])
        elif isinstance(v, (list, dict)):
            ws.append([k, json.dumps(v, ensure_ascii=False)])
        else:
            ws.append([k, v])
    buf = io.BytesIO(); wb.save(buf)
    return out(buf.getvalue(), "data.xlsx",
               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.post("/hindi-ocr")
async def hindi_ocr(file: UploadFile = File(...), lang: str = Form("hin+eng")):
    import pytesseract
    # Windows par Tesseract PATH mein na ho to default install location try karo
    default_win = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if not shutil.which("tesseract") and os.path.exists(default_win):
        pytesseract.pytesseract.tesseract_cmd = default_win

    raw = await file.read()
    if file.filename.lower().endswith(".pdf"):
        doc = open_pdf(raw)
        imgs = [Image.open(io.BytesIO(p.get_pixmap(dpi=200).tobytes("png"))) for p in doc]
        doc.close()
    else:
        imgs = [read_img(raw)]
    try:
        parts = [f"--- Page {i+1} ---\n{pytesseract.image_to_string(im, lang=lang)}" for i, im in enumerate(imgs)]
    except pytesseract.TesseractError as e:
        raise HTTPException(500, f"Tesseract error (Hindi language data installed hai?): {e}")
    return out("\n\n".join(parts).encode("utf-8"), "ocr.txt", "text/plain; charset=utf-8")