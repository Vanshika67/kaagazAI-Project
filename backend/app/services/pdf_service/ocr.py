"""
OCR PDF — makes a scanned (image-only) PDF searchable by running
Tesseract OCR on every page and embedding an invisible text layer
behind the original page image.
"""

from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

from app.utils.file_handler import make_output_path


def ocr_pdf(input_path: Path, language: str = "eng") -> Path:
    doc = fitz.open(str(input_path))

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR accuracy
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        ocr_data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
        scale = pix.width / page.rect.width  # convert image pixels back to PDF points

        for i in range(len(ocr_data["text"])):
            word = ocr_data["text"][i].strip()
            if not word:
                continue

            x = ocr_data["left"][i] / scale
            y = ocr_data["top"][i] / scale
            h = ocr_data["height"][i] / scale

            # Insert an invisible text layer at the word's baseline position
            page.insert_text(
                (x, y + h * 0.85),
                word,
                fontsize=h * 0.8,
                render_mode=3,  # 3 = invisible text (searchable but not visibly drawn)
            )

    output_path = make_output_path("ocr")
    doc.save(str(output_path))
    doc.close()

    return output_path