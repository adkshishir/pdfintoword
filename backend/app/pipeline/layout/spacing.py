"""Compute paragraph spacing and indents from PDF bounding boxes."""

from app.pipeline.models import Block, PageLayout, TextBlock


def apply_layout_spacing(page: PageLayout) -> PageLayout:
    """Set space_before_pt and left_indent_pt from block positions (preserve vertical layout)."""
    blocks = [b for b in page.blocks if isinstance(b, TextBlock)]
    if not blocks:
        return page

    sorted_blocks = sorted(blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
    min_x = min(b.bbox.x0 for b in sorted_blocks)
    prev_bottom: float | None = None

    for block in sorted_blocks:
        block.left_indent_pt = max(0.0, block.bbox.x0 - min_x)
        if prev_bottom is not None:
            gap = block.bbox.y0 - prev_bottom
            block.space_before_pt = max(0.0, gap) if gap > 1.0 else 0.0
        else:
            block.space_before_pt = max(0.0, block.bbox.y0)
        prev_bottom = block.bbox.y1

    return page
