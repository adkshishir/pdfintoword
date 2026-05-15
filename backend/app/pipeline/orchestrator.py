import logging

from app.models.enums import ConversionMode, PdfType
from app.pipeline.detect import detect_pdf_type
from app.pipeline.images.extract import extract_images
from app.pipeline.layout.extractor import extract_layout
from app.pipeline.models import DocumentModel
from app.pipeline.ocr import run_ocr_pipeline
from app.pipeline.structure.reconstructor import reconstruct_structure
from app.pipeline.tables.camelot_extract import extract_tables
from app.pipeline.visual.pipeline import run_visual_reconstruction
from app.utils.headers_footers import detect_headers_footers
from app.word.builder import build_docx
from app.word.grid_renderer import render_document_grid

logger = logging.getLogger(__name__)


class ConversionResult:
    def __init__(
        self,
        docx_bytes: bytes,
        pdf_type: PdfType,
        ocr_used: bool,
        page_count: int,
    ):
        self.docx_bytes = docx_bytes
        self.pdf_type = pdf_type
        self.ocr_used = ocr_used
        self.page_count = page_count


def run_conversion(pdf_bytes: bytes, mode: ConversionMode) -> ConversionResult:
    pdf_type = detect_pdf_type(pdf_bytes, mode)
    ocr_used = False

    if pdf_type in (PdfType.SCANNED, PdfType.MIXED) and mode == ConversionMode.ACCURATE:
        pages, ocr_used = run_ocr_pipeline(pdf_bytes, mode)
    elif pdf_type == PdfType.SCANNED:
        pages, ocr_used = run_ocr_pipeline(pdf_bytes, mode)
    else:
        pages = extract_layout(pdf_bytes, mode)
        if pdf_type == PdfType.MIXED and mode == ConversionMode.ACCURATE:
            ocr_pages, ocr_flag = run_ocr_pipeline(pdf_bytes, mode)
            ocr_used = ocr_flag
            pages = _merge_digital_and_ocr(pages, ocr_pages)

    doc = DocumentModel(
        pages=pages,
        pdf_type=pdf_type.value,
        ocr_used=ocr_used,
    )

    doc = reconstruct_structure(doc, mode)
    doc = detect_headers_footers(doc)
    doc = extract_tables(pdf_bytes, doc, mode)
    doc = extract_images(pdf_bytes, doc, mode)

    if mode == ConversionMode.ACCURATE:
        doc = run_visual_reconstruction(doc, pdf_bytes, mode)
        docx_bytes = render_document_grid(doc)
    else:
        from app.pipeline.layout.backgrounds import apply_background_fills
        from app.pipeline.layout.spacing import apply_layout_spacing

        doc.pages = apply_background_fills(pdf_bytes, doc.pages)
        for i, page in enumerate(doc.pages):
            doc.pages[i] = apply_layout_spacing(page)
        docx_bytes = build_docx(doc, mode)

    return ConversionResult(
        docx_bytes=docx_bytes,
        pdf_type=pdf_type,
        ocr_used=ocr_used,
        page_count=len(pages),
    )


def _merge_digital_and_ocr(digital_pages, ocr_pages):
    merged = []
    for i, d_page in enumerate(digital_pages):
        if d_page.blocks:
            merged.append(d_page)
        elif i < len(ocr_pages):
            merged.append(ocr_pages[i])
        else:
            merged.append(d_page)
    return merged
