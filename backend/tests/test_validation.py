import pytest

from app.services.validation import ValidationError, validate_pdf_content


def test_validate_digital_pdf(digital_pdf_bytes):
    count = validate_pdf_content(digital_pdf_bytes, "application/pdf")
    assert count >= 1


def test_validate_rejects_non_pdf(corrupt_pdf_bytes):
    with pytest.raises(ValidationError):
        validate_pdf_content(corrupt_pdf_bytes)
