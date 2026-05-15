"""Stage 1 — analyze PDF page as visual canvas (margins, columns, zones)."""

from io import BytesIO

import fitz
import pdfplumber

from app.pipeline.canvas_models import ColumnZone, PageCanvas
from app.pipeline.models import BBox, PageLayout, TextBlock


def analyze_page_canvas(
    pdf_bytes: bytes,
    layout: PageLayout,
    strip_headers: bool = False,
) -> PageCanvas:
    blocks = [b for b in layout.blocks if isinstance(b, TextBlock)]
    w, h = layout.width, layout.height

    xs = [b.bbox.x0 for b in blocks] + [b.bbox.x1 for b in blocks]
    ys = [b.bbox.y0 for b in blocks] + [b.bbox.y1 for b in blocks]

    margin_left = min(xs) if xs else 0.0
    margin_right = w - max(xs) if xs else 0.0
    margin_top = min(ys) if ys else 0.0
    margin_bottom = h - max(ys) if ys else 0.0

    columns = _detect_columns(blocks, w, h)

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        if layout.page_num < len(pdf.pages):
            page = pdf.pages[layout.page_num]
            if page.width and page.height:
                w = float(page.width)
                h = float(page.height)

    canvas = PageCanvas(
        page_num=layout.page_num,
        width=w,
        height=h,
        margin_left=max(0, margin_left),
        margin_right=max(0, margin_right),
        margin_top=max(0, margin_top),
        margin_bottom=max(0, margin_bottom),
        columns=columns,
        column_count=max(1, len(columns)),
    )

    if strip_headers:
        _mark_header_footer_zones(layout, canvas)

    return canvas


def _detect_columns(blocks: list[TextBlock], page_w: float, page_h: float) -> list[ColumnZone]:
    if not blocks or page_w <= 0:
        return [ColumnZone(x0=0, x1=page_w, index=0)]

    centers = sorted((b.bbox.x0 + b.bbox.x1) / 2 for b in blocks)
    if len(centers) < 4:
        return [ColumnZone(x0=0, x1=page_w, index=0)]

    gap_threshold = page_w * 0.08
    clusters: list[list[float]] = [[centers[0]]]
    for c in centers[1:]:
        if c - clusters[-1][-1] > gap_threshold:
            clusters.append([c])
        else:
            clusters[-1].append(c)

    if len(clusters) < 2:
        return [ColumnZone(x0=0, x1=page_w, index=0)]

    zones: list[ColumnZone] = []
    for i, cluster in enumerate(clusters):
        cx = sum(cluster) / len(cluster)
        x0 = 0 if i == 0 else (zones[-1].x1 + cx) / 2
        x1 = page_w if i == len(clusters) - 1 else (cx + sum(clusters[i + 1]) / len(clusters[i + 1])) / 2
        zones.append(ColumnZone(x0=x0, x1=x1, index=i))
    return zones


def _mark_header_footer_zones(layout: PageLayout, canvas: PageCanvas) -> None:
    band = canvas.height * 0.1
    for block in layout.blocks:
        if not isinstance(block, TextBlock):
            continue
        if block.bbox.y1 < band:
            block.is_header = True
        if block.bbox.y0 > canvas.height - band:
            block.is_footer = True
