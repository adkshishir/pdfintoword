import fitz
import pdfplumber
from io import BytesIO

from app.models.enums import ConversionMode, PdfType


def detect_pdf_type(pdf_bytes: bytes, mode: ConversionMode) -> PdfType:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = doc.page_count
    sample_pages = (
        list(range(total_pages))
        if mode == ConversionMode.ACCURATE
        else list(range(min(3, total_pages)))
    )

    text_pages = 0
    image_only_pages = 0

    for i in sample_pages:
        page = doc[i]
        text = page.get_text().strip()
        images = page.get_images()
        if len(text) > 50:
            text_pages += 1
        elif images:
            image_only_pages += 1

    doc.close()

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        plumber_text_pages = 0
        pages_to_check = sample_pages
        for i in pages_to_check:
            if i < len(pdf.pages):
                text = pdf.pages[i].extract_text() or ""
                if len(text.strip()) > 50:
                    plumber_text_pages += 1

    has_text = text_pages > 0 or plumber_text_pages > 0
    has_scan = image_only_pages > 0 or (not has_text and total_pages > 0)

    if has_text and has_scan:
        return PdfType.MIXED
    if has_text:
        return PdfType.DIGITAL
    return PdfType.SCANNED
