"""Low-level DOCX XML helpers for shading, borders, anchors, row heights."""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def set_paragraph_shading(paragraph, fill_hex: str) -> None:
    fill = fill_hex.lstrip("#").upper()
    p_pr = paragraph._p.get_or_add_pPr()
    for existing in p_pr.findall(qn("w:shd")):
        p_pr.remove(existing)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def set_cell_shading(cell, fill_hex: str) -> None:
    fill = fill_hex.lstrip("#").upper()
    tc_pr = cell._tc.get_or_add_tcPr()
    for existing in tc_pr.findall(qn("w:shd")):
        tc_pr.remove(existing)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_table_borders_none(table) -> None:
    """Invisible layout grid — no visible borders."""
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    if tbl_pr is None:
        tbl_pr = OxmlElement("w:tblPr")
        tbl.insert(0, tbl_pr)

    for tag in ("w:tblBorders",):
        for existing in tbl_pr.findall(qn(tag)):
            tbl_pr.remove(existing)

    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tbl_pr.append(borders)


def set_row_height(row, height_pt: float) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    for existing in tr_pr.findall(qn("w:trHeight")):
        tr_pr.remove(existing)
    tr_height = OxmlElement("w:trHeight")
    tr_height.set(qn("w:val"), str(int(height_pt * 20)))
    tr_height.set(qn("w:hRule"), "exact")
    tr_pr.append(tr_height)


def set_cell_margins_zero(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    for existing in tc_pr.findall(qn("w:tcMar")):
        tc_pr.remove(existing)
    mar = OxmlElement("w:tcMar")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), "0")
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tc_pr.append(mar)


def add_anchored_picture(run, image_stream, width_emu: int, left_emu: int, top_emu: int) -> None:
    """Anchor image at approximate page coordinates (EMU units)."""
    from docx.shared import Emu

    inline = run.add_picture(image_stream, width=Emu(width_emu))
    inline._inline.graphic.graphicData.pic.nvPicPr.cNvPr.set("name", "LayoutImage")
