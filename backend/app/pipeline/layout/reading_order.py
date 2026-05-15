from app.pipeline.models import Block, BBox


def sort_blocks_reading_order(blocks: list[Block]) -> list[Block]:
    """Sort blocks top-to-bottom, left-to-right with simple column detection."""

    if not blocks:
        return blocks

    def center_x(b: Block) -> float:
        return (b.bbox.x0 + b.bbox.x1) / 2

    xs = [center_x(b) for b in blocks]
    if len(xs) >= 2:
        mid = (min(xs) + max(xs)) / 2
        left = [b for b in blocks if center_x(b) <= mid]
        right = [b for b in blocks if center_x(b) > mid]
        if left and right and len(left) >= 2 and len(right) >= 2:
            left.sort(key=lambda b: (b.bbox.y0, b.bbox.x0))
            right.sort(key=lambda b: (b.bbox.y0, b.bbox.x0))
            return left + right

    return sorted(blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))


def merge_nearby_lines(blocks: list[Block], y_threshold: float = 5.0) -> list[Block]:
    from app.pipeline.models import TextBlock

    text_blocks = [b for b in blocks if isinstance(b, TextBlock)]
    other = [b for b in blocks if not isinstance(b, TextBlock)]
    if not text_blocks:
        return blocks

    merged: list[TextBlock] = []
    current: TextBlock | None = None

    for block in sorted(text_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0)):
        if current is None:
            current = block.model_copy()
            continue
        same_line = abs(block.bbox.y0 - current.bbox.y0) < y_threshold
        if same_line and block.font_size == current.font_size:
            current.text = f"{current.text} {block.text}".strip()
            if block.spans:
                current.spans.extend(block.spans)
            current.bbox = BBox(
                x0=min(current.bbox.x0, block.bbox.x0),
                y0=min(current.bbox.y0, block.bbox.y0),
                x1=max(current.bbox.x1, block.bbox.x1),
                y1=max(current.bbox.y1, block.bbox.y1),
            )
        else:
            merged.append(current)
            current = block.model_copy()

    if current:
        merged.append(current)

    return sort_blocks_reading_order(merged + other)
