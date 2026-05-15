"""Stage 3 — column-aware reading flow reconstruction."""

from app.pipeline.canvas_models import PageCanvas
from app.pipeline.models import Block, ImageBlock, PageLayout, TableBlock, TextBlock


def _column_index(canvas: PageCanvas, block: Block) -> int:
    cx = (block.bbox.x0 + block.bbox.x1) / 2
    for col in canvas.columns:
        if col.x0 <= cx <= col.x1:
            return col.index
    return 0


def compute_reading_order(layout: PageLayout) -> list[int]:
    """Return block indices in natural reading order (column-aware)."""
    canvas = layout.canvas
    indexed = list(enumerate(layout.blocks))

    if canvas and canvas.column_count > 1:
        indexed.sort(
            key=lambda pair: (
                _column_index(canvas, pair[1]),
                pair[1].bbox.y0,
                pair[1].bbox.x0,
            )
        )
    else:
        indexed.sort(key=lambda pair: (pair[1].bbox.y0, pair[1].bbox.x0))

    return [i for i, _ in indexed]


def reorder_blocks(layout: PageLayout) -> PageLayout:
    order = compute_reading_order(layout)
    layout.reading_order = order
    layout.blocks = [layout.blocks[i] for i in order]
    return layout


def classify_block_zones(layout: PageLayout) -> PageLayout:
    """Stage 2 supplement — heading/list/sidebar from geometry + typography."""
    if not layout.canvas:
        return layout

    body_blocks = [b for b in layout.blocks if isinstance(b, TextBlock)]
    sizes = [b.font_size for b in body_blocks if b.font_size]
    median = sorted(sizes)[len(sizes) // 2] if sizes else 12.0
    page_w = layout.canvas.width

    for block in layout.blocks:
        if isinstance(block, TextBlock):
            text = block.text.strip()
            if block.is_header:
                block.type = "header"
            elif block.is_footer:
                block.type = "footer"
            elif block.bbox.x0 > page_w * 0.72 and len(text) < 120:
                block.type = "text"
            elif block.font_size >= median * 1.35 or (block.bold and block.font_size >= median):
                block.type = "heading"
                block.level = 1 if block.font_size < median * 1.6 else 2
            elif text.startswith(("•", "-", "*", "·")) or (
                len(text) > 2 and text[0].isdigit() and text[1] in ".)"
            ):
                block.type = "list_item"
        elif isinstance(block, TableBlock):
            pass
        elif isinstance(block, ImageBlock):
            pass

    return layout
