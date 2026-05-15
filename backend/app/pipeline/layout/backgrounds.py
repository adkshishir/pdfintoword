"""Extract filled rectangles (colors / patterns) from PDF vector drawings."""

import logging

import fitz

from app.pipeline.layout.colors import int_to_hex, normalize_hex
from app.pipeline.models import BBox, PageLayout, TextBlock

logger = logging.getLogger(__name__)


def _rect_from_draw(item: dict) -> tuple[float, float, float, float] | None:
    rect = item.get("rect")
    if rect and len(rect) >= 4:
        return float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])
    return None


def _fill_color_hex(item: dict) -> str | None:
    fill = item.get("fill")
    if fill is None:
        return None
    if isinstance(fill, (list, tuple)) and len(fill) >= 3:
        r, g, b = fill[0], fill[1], fill[2]
        if all(isinstance(v, float) and v <= 1.0 for v in (r, g, b)):
            return normalize_hex(f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}")
        return normalize_hex(f"#{int(r):02X}{int(g):02X}{int(b):02X}")
    if isinstance(fill, (int, float)):
        return int_to_hex(int(fill))
    return None


def _overlap_ratio(inner: BBox, outer: tuple[float, float, float, float]) -> float:
    ox0, oy0, ox1, oy1 = outer
    ix0, iy0, ix1, iy1 = inner.x0, inner.y0, inner.x1, inner.y1
    inter_x0 = max(ix0, ox0)
    inter_y0 = max(iy0, oy0)
    inter_x1 = min(ix1, ox1)
    inter_y1 = min(iy1, oy1)
    if inter_x1 <= inter_x0 or inter_y1 <= inter_y0:
        return 0.0
    inter_area = (inter_x1 - inter_x0) * (inter_y1 - inter_y0)
    inner_area = max((ix1 - ix0) * (iy1 - iy0), 1.0)
    return inter_area / inner_area


def apply_background_fills(pdf_bytes: bytes, pages: list[PageLayout]) -> list[PageLayout]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for layout in pages:
            if layout.page_num >= doc.page_count:
                continue
            page = doc[layout.page_num]
            fills: list[tuple[tuple[float, float, float, float], str]] = []
            try:
                for drawing in page.get_drawings():
                    rect = _rect_from_draw(drawing)
                    color = _fill_color_hex(drawing)
                    if rect and color:
                        w = rect[2] - rect[0]
                        h = rect[3] - rect[1]
                        if w > 4 and h > 4:
                            fills.append((rect, color))
            except Exception as exc:
                logger.debug("get_drawings failed page %s: %s", layout.page_num, exc)

            for block in layout.blocks:
                if not isinstance(block, TextBlock):
                    continue
                best_color: str | None = None
                best_ratio = 0.0
                for rect, color in fills:
                    ratio = _overlap_ratio(block.bbox, rect)
                    if ratio > best_ratio and ratio > 0.25:
                        best_ratio = ratio
                        best_color = color
                if best_color:
                    block.background_color = best_color
    finally:
        doc.close()
    return pages
