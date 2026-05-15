"""Convert PDF points to Word dimensions."""

from docx.shared import Inches, Pt

# Usable text width on default Letter (1" margins each side)
DOCX_CONTENT_WIDTH_IN = 6.5


def page_content_width_in(page_width_pt: float) -> float:
    if page_width_pt <= 0:
        return DOCX_CONTENT_WIDTH_IN
    page_width_in = page_width_pt / 72.0
    return min(DOCX_CONTENT_WIDTH_IN, page_width_in * 0.92)


def pt_to_docx_indent(pt: float, page_width_pt: float) -> Pt:
    scale = page_content_width_in(page_width_pt) / (page_width_pt / 72.0) if page_width_pt else 1.0
    return Pt(min(pt * scale, 400))


def pt_to_space_before(pt: float) -> Pt:
    return Pt(min(max(pt, 0), 72))


def bbox_width_inches(bbox_width_pt: float, page_width_pt: float) -> float:
    if page_width_pt <= 0:
        return 4.0
    ratio = bbox_width_pt / page_width_pt
    return min(page_content_width_in(page_width_pt) * ratio, DOCX_CONTENT_WIDTH_IN)
