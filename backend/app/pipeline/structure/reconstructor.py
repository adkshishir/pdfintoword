from app.models.enums import ConversionMode
from app.pipeline.models import DocumentModel, PageLayout, TextBlock


def reconstruct_structure(doc: DocumentModel, mode: ConversionMode) -> DocumentModel:
    for page in doc.pages:
        page.blocks = _process_page_blocks(page, mode)
    return doc


def _process_page_blocks(page: PageLayout, mode: ConversionMode) -> list:
    processed = []
    body_font_sizes: list[float] = []

    for block in page.blocks:
        if isinstance(block, TextBlock):
            body_font_sizes.append(block.font_size)

    median_size = sorted(body_font_sizes)[len(body_font_sizes) // 2] if body_font_sizes else 12.0

    for block in page.blocks:
        if not isinstance(block, TextBlock):
            processed.append(block)
            continue

        text = block.text.strip()
        if not text:
            continue

        if mode == ConversionMode.ACCURATE:
            if block.font_size >= median_size * 1.35 or (block.bold and block.font_size >= median_size):
                block.type = "heading"
                block.level = 1 if block.font_size < median_size * 1.6 else 2
            elif text.startswith(("•", "-", "*", "·")) or (
                len(text) > 2 and text[0].isdigit() and text[1] in ".)"
            ):
                block.type = "list_item"
            else:
                block.type = "text"
        else:
            block.type = "text"

        processed.append(block)

    return processed
