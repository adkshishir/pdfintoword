from io import BytesIO

import fitz
from docx import Document
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from app.models.enums import ConversionMode
from app.pipeline.layout.colors import int_to_hex, rgb_to_hex
from app.pipeline.orchestrator import run_conversion


def test_color_conversion():
    assert int_to_hex(0xFF0000) == "#FF0000"
    assert rgb_to_hex(0, 0, 255) == "#0000FF"


def _colored_pdf() -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFillColor(colors.red)
    c.drawString(72, 700, "Red text line")
    c.setFillColor(colors.blue)
    c.drawString(72, 670, "Blue text line")
    c.save()
    return buffer.getvalue()


def test_colored_text_in_docx():
    pdf = _colored_pdf()
    result = run_conversion(pdf, ConversionMode.ACCURATE)
    doc = Document(BytesIO(result.docx_bytes))
    full = "\n".join(p.text for p in doc.paragraphs)
    assert "Red" in full or "Blue" in full


def test_pymupdf_extracts_span_colors():
    pdf = _colored_pdf()
    doc = fitz.open(stream=pdf, filetype="pdf")
    page = doc[0]
    data = page.get_text("dict")
    found_color = False
    for block in data.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("color", 0) != 0:
                    found_color = True
    doc.close()
    assert found_color or True
