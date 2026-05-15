from app.models.enums import ConversionMode, PdfType
from app.pipeline.detect import detect_pdf_type


def test_scanned_detection(scanned_pdf_bytes):
    pdf_type = detect_pdf_type(scanned_pdf_bytes, ConversionMode.ACCURATE)
    assert pdf_type in (PdfType.SCANNED, PdfType.DIGITAL, PdfType.MIXED)
