from __future__ import annotations

import io
from pathlib import Path

import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def extract_text_from_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if suffix == ".pdf":
        text = _extract_text_from_pdf(file_bytes)
    elif suffix in SUPPORTED_IMAGE_EXTENSIONS:
        text = _extract_text_from_image(file_bytes)
    else:
        raise ValueError("Unsupported file type. Please upload PDF, PNG, or JPG.")

    if not text.strip():
        raise ValueError(
            "OCR returned no text. Try a higher-quality scan or a machine-readable PDF."
        )
    return text


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    extracted = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted.append(page.extract_text() or "")

    text = "\n".join(extracted).strip()
    if text:
        return text

    images = convert_from_bytes(file_bytes, first_page=1, last_page=3)
    ocr_text = "\n".join(pytesseract.image_to_string(image) for image in images)
    return ocr_text


def _extract_text_from_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image)


def load_preview_images(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if suffix == ".pdf":
        return convert_from_bytes(file_bytes, first_page=1, last_page=2)
    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        return [Image.open(io.BytesIO(file_bytes))]
    return []
