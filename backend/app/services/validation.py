import io

import fitz

from app.config import get_settings

PDF_MAGIC = b"%PDF"


class ValidationError(Exception):
    pass


def validate_pdf_content(data: bytes, content_type: str | None = None) -> int:
    settings = get_settings()

    if len(data) > settings.max_upload_bytes:
        raise ValidationError(f"File exceeds maximum size of {settings.max_upload_mb} MB")

    if not data.startswith(PDF_MAGIC):
        raise ValidationError("File is not a valid PDF")

    if content_type and "pdf" not in content_type.lower():
        raise ValidationError("Invalid content type; expected application/pdf")

    try:
        doc = fitz.open(stream=data, filetype="pdf")
        page_count = doc.page_count
        if page_count == 0:
            raise ValidationError("PDF has no pages")
        if page_count > settings.max_pdf_pages:
            raise ValidationError(f"PDF exceeds maximum of {settings.max_pdf_pages} pages")
        doc.close()
        return page_count
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(f"Invalid or corrupt PDF: {exc}") from exc


def malware_scan_stub(data: bytes) -> bool:
    """Placeholder for optional malware scanning."""
    _ = data
    return True
