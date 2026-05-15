import logging
from io import BytesIO

import pytesseract
from PIL import Image

from app.pipeline.layout.reading_order import sort_blocks_reading_order
from app.pipeline.models import BBox, PageLayout, TextBlock

logger = logging.getLogger(__name__)


def ocr_page_tesseract(image_bytes: bytes, page_num: int, width: float, height: float) -> PageLayout:
    layout = PageLayout(page_num=page_num, width=width, height=height, blocks=[])

    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        n = len(data["text"])
        for i in range(n):
            text = (data["text"][i] or "").strip()
            conf = int(data["conf"][i]) if data["conf"][i] != "-1" else -1
            if not text or conf < 50:
                continue
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            layout.blocks.append(
                TextBlock(
                    text=text,
                    bbox=BBox(x0=x, y0=y, x1=x + w, y1=y + h),
                    font_size=12.0,
                )
            )
    except Exception as exc:
        logger.warning("Tesseract failed for page %s: %s", page_num, exc)

    layout.blocks = sort_blocks_reading_order(layout.blocks)
    return layout
