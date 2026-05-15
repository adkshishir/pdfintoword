"""Visual document reconstruction pipeline (canvas → grid → DOCX-ready layout)."""

from app.models.enums import ConversionMode
from app.pipeline.models import DocumentModel, PageLayout
from app.pipeline.grid.engine import build_page_grid
from app.pipeline.layout.backgrounds import apply_background_fills
from app.pipeline.page_analysis import analyze_page_canvas
from app.pipeline.visual.reading_flow import classify_block_zones, reorder_blocks


def run_visual_reconstruction(
    doc: DocumentModel,
    pdf_bytes: bytes,
    mode: ConversionMode,
    strip_repeated_headers: bool = False,
) -> DocumentModel:
    """Stages 1–5, 8: page analysis → reading flow → grid mapping."""
    doc.use_visual_grid = mode == ConversionMode.ACCURATE

    for i, page in enumerate(doc.pages):
        layout = PageLayout(
            page_num=page.page_num,
            width=page.width,
            height=page.height,
            blocks=page.blocks,
            canvas=getattr(page, "canvas", None),
            grid=getattr(page, "grid", None),
            reading_order=getattr(page, "reading_order", []),
        )

        layout.canvas = analyze_page_canvas(
            pdf_bytes, layout, strip_headers=strip_repeated_headers
        )
        layout = classify_block_zones(layout)
        layout = reorder_blocks(layout)
        layout.grid = build_page_grid(layout)
        doc.pages[i] = layout

    doc.pages = apply_background_fills(pdf_bytes, doc.pages)
    return doc
