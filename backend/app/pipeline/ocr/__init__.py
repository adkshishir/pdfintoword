import logging
from io import BytesIO

import fitz
from pdf2image import convert_from_bytes

from app.models.enums import ConversionMode
from app.pipeline.layout.reading_order import sort_blocks_reading_order
from app.pipeline.models import PageLayout
from app.pipeline.ocr.paddle import ocr_page_image
from app.pipeline.ocr.tesseract import ocr_page_tesseract

logger = logging.getLogger(__name__)


def run_ocr_pipeline(pdf_bytes: bytes, mode: ConversionMode) -> tuple[list[PageLayout], bool]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = doc.page_count
    widths = [doc[i].rect.width for i in range(page_count)]
    heights = [doc[i].rect.height for i in range(page_count)]
    doc.close()

    dpi = 200 if mode == ConversionMode.ACCURATE else 150
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    pages: list[PageLayout] = []
    ocr_used = False

    for i, pil_image in enumerate(images):
        buf = BytesIO()
        pil_image.save(buf, format="PNG")
        image_bytes = buf.getvalue()
        width = widths[i] if i < len(widths) else float(pil_image.width)
        height = heights[i] if i < len(heights) else float(pil_image.height)

        try:
            layout = ocr_page_image(image_bytes, i, width, height)
            ocr_used = True
        except Exception:
            logger.info("Falling back to Tesseract for page %s", i)
            layout = ocr_page_tesseract(image_bytes, i, width, height)
            ocr_used = True

        layout.blocks = sort_blocks_reading_order(layout.blocks)
        pages.append(layout)

    return pages, ocr_used
