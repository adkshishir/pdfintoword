import io
import sys
from pathlib import Path

import fitz
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)


@pytest.fixture
def digital_pdf_bytes() -> bytes:
  path = FIXTURES_DIR / "digital_sample.pdf"
  if path.exists():
    return path.read_bytes()
  buffer = io.BytesIO()
  c = canvas.Canvas(buffer, pagesize=letter)
  c.setFont("Helvetica-Bold", 16)
  c.drawString(72, 750, "PDFintoWord Test Document")
  c.setFont("Helvetica", 12)
  c.drawString(72, 720, "This is a digital PDF with extractable text.")
  c.drawString(72, 700, "Second paragraph for layout testing.")
  c.drawString(72, 680, "Name")
  c.drawString(200, 680, "Value")
  c.drawString(72, 660, "Item A")
  c.drawString(200, 660, "100")
  c.showPage()
  c.setFont("Helvetica", 12)
  c.drawString(72, 750, "Page two content for multi-page test.")
  c.save()
  data = buffer.getvalue()
  path.write_bytes(data)
  return data


@pytest.fixture
def scanned_pdf_bytes() -> bytes:
  path = FIXTURES_DIR / "scanned_sample.pdf"
  if path.exists():
    return path.read_bytes()
  doc = fitz.open()
  page = doc.new_page(width=612, height=792)
  page.insert_text((72, 100), "Scanned-like PDF with minimal text layer", fontsize=8)
  data = doc.tobytes()
  doc.close()
  path.write_bytes(data)
  return data


@pytest.fixture
def corrupt_pdf_bytes() -> bytes:
  return b"%PDF-1.4\n%corrupt content"
