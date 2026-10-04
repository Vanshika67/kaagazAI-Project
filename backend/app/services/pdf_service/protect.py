"""
Protect PDF — adds a password (encrypts the PDF).
Unlock PDF — removes the password (decrypts the PDF), given the correct password.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.utils.file_handler import make_output_path


def protect_pdf(input_path: Path, password: str) -> Path:
    if not password:
        raise ValueError("Password cannot be empty.")

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    output_path = make_output_path("protected")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def unlock_pdf(input_path: Path, password: str) -> Path:
    reader = PdfReader(str(input_path))

    if reader.is_encrypted:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError("Incorrect password — could not unlock the PDF.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    output_path = make_output_path("unlocked")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path