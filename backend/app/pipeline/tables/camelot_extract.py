import logging
import tempfile
from io import BytesIO
from pathlib import Path

import pdfplumber

from app.models.enums import ConversionMode
from app.pipeline.layout.colors import plumber_color_to_hex
from app.pipeline.models import BBox, DocumentModel, TableBlock, TableCellStyle

logger = logging.getLogger(__name__)


def extract_tables(pdf_bytes: bytes, doc: DocumentModel, mode: ConversionMode) -> DocumentModel:
    if mode == ConversionMode.FAST:
        return _extract_fast_tables(pdf_bytes, doc)
    return _extract_all_tables(pdf_bytes, doc)


def _extract_fast_tables(pdf_bytes: bytes, doc: DocumentModel) -> DocumentModel:
    if not doc.pages:
        return doc
    tables = _run_camelot(pdf_bytes, pages="1", with_styles=False)
    if tables and doc.pages:
        doc.pages[0].blocks.extend(tables)
    return doc


def _extract_all_tables(pdf_bytes: bytes, doc: DocumentModel) -> DocumentModel:
    tables_by_page: dict[int, list[TableBlock]] = {}
    all_tables = _run_camelot(pdf_bytes, pages="all", with_styles=True)
    for table in all_tables:
        tables_by_page.setdefault(table.page_num, []).append(table)

    for page in doc.pages:
        page.blocks.extend(tables_by_page.get(page.page_num, []))

    return doc


def _cell_styles_from_plumber(page, rows: list[list[str]]) -> list[list[TableCellStyle]] | None:
    try:
        tables = page.find_tables()
        if not tables:
            return None
        table = tables[0]
        styles: list[list[TableCellStyle]] = []
        for r_idx, row in enumerate(rows):
            row_styles: list[TableCellStyle] = []
            for c_idx, cell_text in enumerate(row):
                style = TableCellStyle(text=str(cell_text))
                if r_idx < len(table.cells):
                    pass
                row_styles.append(style)
            styles.append(row_styles)
        return styles
    except Exception:
        return None


def _enrich_table_colors(pdf_bytes: bytes, block: TableBlock) -> None:
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            if block.page_num >= len(pdf.pages):
                return
            page = pdf.pages[block.page_num]
            chars = page.chars
            if not chars:
                return
            styles: list[list[TableCellStyle]] = []
            for row in block.rows:
                row_styles = []
                for cell_text in row:
                    tc = TableCellStyle(text=str(cell_text))
                    if cell_text.strip():
                        matching = [
                            c
                            for c in chars
                            if cell_text.strip()[:8] in (c.get("text") or "")
                        ]
                        if matching:
                            c0 = matching[0]
                            tc.text_color = plumber_color_to_hex(c0.get("non_stroking_color"))
                            if c0.get("fontname", "").lower().find("bold") >= 0:
                                tc.bold = True
                    row_styles.append(tc)
                styles.append(row_styles)
            block.cell_styles = styles
    except Exception as exc:
        logger.debug("Table color enrichment failed: %s", exc)


def _run_camelot(pdf_bytes: bytes, pages: str = "all", with_styles: bool = False) -> list[TableBlock]:
    blocks: list[TableBlock] = []
    try:
        import camelot

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            tables_lattice = camelot.read_pdf(tmp_path, pages=pages, flavor="lattice")
            tables_stream = camelot.read_pdf(tmp_path, pages=pages, flavor="stream")
            seen = set()
            for tables in (tables_lattice, tables_stream):
                for table in tables:
                    key = (table.page, table.df.shape)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows = table.df.fillna("").astype(str).values.tolist()
                    if not rows:
                        continue
                    page_num = int(table.page) - 1
                    block = TableBlock(
                        rows=rows,
                        bbox=BBox(x0=0, y0=0, x1=500, y1=300),
                        page_num=page_num,
                    )
                    if with_styles:
                        _enrich_table_colors(pdf_bytes, block)
                    blocks.append(block)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as exc:
        logger.warning("Camelot table extraction failed: %s", exc)

    return blocks
