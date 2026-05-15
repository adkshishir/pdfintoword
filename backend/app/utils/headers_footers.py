from collections import Counter

from app.pipeline.models import DocumentModel, TextBlock


def detect_headers_footers(doc: DocumentModel, band_ratio: float = 0.1) -> DocumentModel:
    """Mark repeated top/bottom text across pages as header/footer."""
    top_texts: Counter[str] = Counter()
    bottom_texts: Counter[str] = Counter()

    for page in doc.pages:
        if not page.blocks:
            continue
        band_height = page.height * band_ratio
        for block in page.blocks:
            if not isinstance(block, TextBlock):
                continue
            text_norm = block.text.strip().lower()
            if not text_norm or len(text_norm) < 3:
                continue
            if block.bbox.y0 < band_height:
                top_texts[text_norm] += 1
            if block.bbox.y1 > page.height - band_height:
                bottom_texts[text_norm] += 1

    repeated_top = {t for t, c in top_texts.items() if c >= 2}
    repeated_bottom = {t for t, c in bottom_texts.items() if c >= 2}

    for page in doc.pages:
        band_height = page.height * band_ratio
        for block in page.blocks:
            if not isinstance(block, TextBlock):
                continue
            text_norm = block.text.strip().lower()
            if block.bbox.y0 < band_height and text_norm in repeated_top:
                block.is_header = True
            if block.bbox.y1 > page.height - band_height and text_norm in repeated_bottom:
                block.is_footer = True

    return doc
