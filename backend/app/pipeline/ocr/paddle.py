import logging
from typing import Any

from app.pipeline.models import BBox, PageLayout, TextBlock

logger = logging.getLogger(__name__)

_ocr_engine: Any = None


def _get_paddle_ocr() -> Any:
    global _ocr_engine
    if _ocr_engine is None:
        from paddleocr import PaddleOCR

        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _ocr_engine


def ocr_page_image(image_bytes: bytes, page_num: int, width: float, height: float) -> PageLayout:
    import numpy as np
    from PIL import Image
    from io import BytesIO

    layout = PageLayout(page_num=page_num, width=width, height=height, blocks=[])

    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
        ocr = _get_paddle_ocr()
        result = ocr.ocr(arr, cls=True)
        if not result or not result[0]:
            return layout

        for line in result[0]:
            box, (text, confidence) = line
            if confidence < 0.5 or not text.strip():
                continue
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            layout.blocks.append(
                TextBlock(
                    text=text.strip(),
                    bbox=BBox(x0=min(xs), y0=min(ys), x1=max(xs), y1=max(ys)),
                    font_size=12.0,
                )
            )
    except Exception as exc:
        logger.warning("PaddleOCR failed for page %s: %s", page_num, exc)
        raise

    return layout
