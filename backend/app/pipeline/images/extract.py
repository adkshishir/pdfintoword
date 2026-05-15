import logging
from io import BytesIO

import fitz

from app.models.enums import ConversionMode
from app.pipeline.models import BBox, DocumentModel, ImageBlock

logger = logging.getLogger(__name__)


def extract_images(pdf_bytes: bytes, doc: DocumentModel, mode: ConversionMode) -> DocumentModel:
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_layout in doc.pages:
        if page_layout.page_num >= pdf_doc.page_count:
            continue
        page = pdf_doc[page_layout.page_num]
        existing_image_areas = {
            (round(b.bbox.x0), round(b.bbox.y0))
            for b in page_layout.blocks
            if isinstance(b, ImageBlock)
        }

        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                base_image = pdf_doc.extract_image(xref)
                if not base_image:
                    continue
                image_bytes = base_image["image"]
                width = base_image.get("width", 100)
                height = base_image.get("height", 100)

                rects = page.get_image_rects(xref)
                if rects:
                    rect = rects[0]
                    bbox = BBox(x0=rect.x0, y0=rect.y0, x1=rect.x1, y1=rect.y1)
                else:
                    bbox = BBox(x0=50, y0=50, x1=50 + width, y1=50 + height)

                key = (round(bbox.x0), round(bbox.y0))
                if key in existing_image_areas:
                    continue

                page_layout.blocks.append(
                    ImageBlock(
                        data=image_bytes,
                        bbox=bbox,
                        width=int(width),
                        height=int(height),
                        page_num=page_layout.page_num,
                    )
                )
                existing_image_areas.add(key)
            except Exception as exc:
                logger.debug("Failed to extract image xref %s: %s", xref, exc)

        if mode == ConversionMode.ACCURATE and not any(
            isinstance(b, ImageBlock) for b in page_layout.blocks
        ):
            _render_page_snapshot(page, page_layout)

    pdf_doc.close()
    return doc


def _render_page_snapshot(page: fitz.Page, page_layout) -> None:
    try:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        image_bytes = pix.tobytes("png")
        page_layout.blocks.append(
            ImageBlock(
                data=image_bytes,
                bbox=BBox(x0=0, y0=0, x1=page.rect.width, y1=page.rect.height),
                width=int(pix.width),
                height=int(pix.height),
                page_num=page_layout.page_num,
            )
        )
    except Exception as exc:
        logger.debug("Page render snapshot failed: %s", exc)
