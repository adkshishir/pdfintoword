import fitz
from io import BytesIO

import pdfplumber

from app.models.enums import ConversionMode
from app.pipeline.layout.colors import int_to_hex, normalize_hex
from app.pipeline.layout.reading_order import merge_nearby_lines, sort_blocks_reading_order
from app.pipeline.layout.spacing import apply_layout_spacing
from app.pipeline.models import BBox, PageLayout, TextBlock, TextSpan


def _span_from_fitz(span: dict) -> TextSpan:
    flags = span.get("flags", 0)
    color = int_to_hex(span.get("color", 0))
    return TextSpan(
        text=span.get("text", ""),
        font_size=float(span.get("size", 12.0)),
        bold=bool(flags & 2**4),
        italic=bool(flags & 2**1),
        underline=bool(flags & 2**0),
        color=color,
        font_name=span.get("font"),
    )


def _line_to_text_block(line: dict, page_width: float) -> TextBlock | None:
    spans_raw = line.get("spans", [])
    spans: list[TextSpan] = []
    for s in spans_raw:
        ts = _span_from_fitz(s)
        if ts.text:
            spans.append(ts)
    if not spans:
        return None

    text = "".join(s.text for s in spans).strip()
    if not text:
        return None

    bbox_line = line.get("bbox", [0, 0, 0, 0])
    dominant = max(spans, key=lambda s: len(s.text))
    x0, y0, x1, y1 = bbox_line[0], bbox_line[1], bbox_line[2], bbox_line[3]

    alignment = "left"
    if page_width > 0:
        cx = (x0 + x1) / 2
        if cx > page_width * 0.65:
            alignment = "right"
        elif page_width * 0.35 < cx < page_width * 0.65:
            alignment = "center"

    return TextBlock(
        text=text,
        spans=spans,
        bbox=BBox(x0=x0, y0=y0, x1=x1, y1=y1),
        font_size=dominant.font_size,
        bold=dominant.bold,
        italic=dominant.italic,
        underline=dominant.underline,
        color=dominant.color,
        font_name=dominant.font_name,
        alignment=alignment,
    )


def extract_layout(pdf_bytes: bytes, mode: ConversionMode) -> list[PageLayout]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[PageLayout] = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        rect = page.rect
        layout = PageLayout(
            page_num=page_num,
            width=rect.width,
            height=rect.height,
            blocks=[],
        )

        if mode == ConversionMode.ACCURATE:
            blocks = _extract_detailed_blocks(page)
        else:
            blocks = _extract_fast_blocks(page)

        layout.blocks = merge_nearby_lines(sort_blocks_reading_order(blocks))
        layout = apply_layout_spacing(layout)
        pages.append(layout)

    doc.close()

    if mode == ConversionMode.ACCURATE:
        pages = _enrich_with_pdfplumber(pdf_bytes, pages)

    return pages


def _extract_fast_blocks(page: fitz.Page) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    data = page.get_text("dict")
    page_width = page.rect.width

    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            tb = _line_to_text_block(line, page_width)
            if tb:
                blocks.append(tb)

    if blocks:
        return blocks

    for item in page.get_text("blocks"):
        if len(item) < 5:
            continue
        x0, y0, x1, y1, content = item[0], item[1], item[2], item[3], item[4]
        content = str(content).strip()
        if content:
            blocks.append(
                TextBlock(
                    text=content,
                    bbox=BBox(x0=x0, y0=y0, x1=x1, y1=y1),
                    font_size=12.0,
                    spans=[TextSpan(text=content, font_size=12.0)],
                )
            )
    return blocks


def _extract_detailed_blocks(page: fitz.Page) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    page_width = page.rect.width
    data = page.get_text("dict")

    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            tb = _line_to_text_block(line, page_width)
            if tb:
                blocks.append(tb)

    return blocks


def _enrich_with_pdfplumber(pdf_bytes: bytes, pages: list[PageLayout]) -> list[PageLayout]:
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for layout in pages:
            if layout.page_num >= len(pdf.pages):
                continue
            if layout.blocks:
                continue
            plumber_page = pdf.pages[layout.page_num]
            text = plumber_page.extract_text() or ""
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    layout.blocks.append(
                        TextBlock(
                            text=line,
                            bbox=BBox(x0=50, y0=50, x1=500, y1=70),
                            font_size=12.0,
                            spans=[TextSpan(text=line, font_size=12.0)],
                        )
                    )
    return pages
