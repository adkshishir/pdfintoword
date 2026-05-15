"""Stage 5 & 8 — virtual layout grid + mathematical spacing preservation."""

from app.pipeline.canvas_models import GridPlacement, PageGrid
from app.pipeline.models import Block, PageLayout

MAX_ROWS = 120
MAX_COLS = 24
MERGE_THRESHOLD_PT = 4.0
MIN_ROW_HEIGHT_PT = 6.0


def _cluster(values: list[float], threshold: float) -> list[float]:
    if not values:
        return [0.0]
    sorted_v = sorted(values)
    clusters: list[list[float]] = [[sorted_v[0]]]
    for v in sorted_v[1:]:
        if v - clusters[-1][-1] > threshold:
            clusters.append([v])
        else:
            clusters[-1].append(v)
    return [sum(c) / len(c) for c in clusters]


def _simplify_lines(lines: list[float], max_count: int) -> list[float]:
    if len(lines) <= max_count:
        return lines
    step = max(1, (len(lines) - 1) // (max_count - 1))
    reduced = [lines[i] for i in range(0, len(lines), step)]
    if reduced[-1] != lines[-1]:
        reduced.append(lines[-1])
    return reduced


def _boundaries_from_blocks(blocks: list[Block], page_w: float, page_h: float) -> tuple[list[float], list[float]]:
    y_vals: list[float] = [0.0, page_h]
    x_vals: list[float] = [0.0, page_w]
    for b in blocks:
        y_vals.extend([b.bbox.y0, b.bbox.y1])
        x_vals.extend([b.bbox.x0, b.bbox.x1])

    row_lines = _cluster(y_vals, MERGE_THRESHOLD_PT)
    col_lines = _cluster(x_vals, MERGE_THRESHOLD_PT)

    if len(row_lines) > MAX_ROWS:
        row_lines = _simplify_lines(row_lines, MAX_ROWS)
    if len(col_lines) > MAX_COLS:
        col_lines = _simplify_lines(col_lines, MAX_COLS)
    return row_lines, col_lines


def _band_index(value: float, boundaries: list[float]) -> int:
    for i in range(len(boundaries) - 1):
        if boundaries[i] <= value <= boundaries[i + 1]:
            return i
    return max(0, len(boundaries) - 2)


def build_page_grid(layout: PageLayout) -> PageGrid:
    blocks = layout.blocks
    page_w, page_h = layout.width, layout.height

    row_lines, col_lines = _boundaries_from_blocks(blocks, page_w, page_h)
    n_rows = max(1, len(row_lines) - 1)
    n_cols = max(1, len(col_lines) - 1)

    row_heights = [max(MIN_ROW_HEIGHT_PT, row_lines[i + 1] - row_lines[i]) for i in range(n_rows)]
    col_widths = [max(1.0, col_lines[i + 1] - col_lines[i]) for i in range(n_cols)]

    placements: list[GridPlacement] = []
    prev_bottom = 0.0
    order = layout.reading_order if layout.reading_order else list(range(len(blocks)))

    for bi in order:
        if bi >= len(blocks):
            continue
        block = blocks[bi]

        gap = block.bbox.y0 - prev_bottom
        if gap > MERGE_THRESHOLD_PT * 2 and prev_bottom > 0:
            placements.append(
                GridPlacement(
                    row=min(len(placements), n_rows - 1),
                    col=0,
                    colspan=n_cols,
                    block_index=-1,
                    is_spacer=True,
                    spacer_height_pt=gap,
                )
            )

        r0 = _band_index(block.bbox.y0, row_lines)
        r1 = _band_index(block.bbox.y1, row_lines)
        c0 = _band_index(block.bbox.x0, col_lines)
        c1 = _band_index(block.bbox.x1, col_lines)
        if r1 < r0:
            r1 = r0
        if c1 < c0:
            c1 = c0

        placements.append(
            GridPlacement(
                row=r0,
                col=c0,
                rowspan=max(1, r1 - r0 + 1),
                colspan=max(1, c1 - c0 + 1),
                block_index=bi,
            )
        )
        prev_bottom = max(prev_bottom, block.bbox.y1)

    return PageGrid(
        row_count=n_rows,
        col_count=n_cols,
        row_heights_pt=row_heights,
        col_widths_pt=col_widths,
        placements=placements,
        row_boundaries=row_lines,
        col_boundaries=col_lines,
    )
