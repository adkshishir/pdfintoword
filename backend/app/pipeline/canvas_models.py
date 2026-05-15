"""Visual canvas & grid models for mirror-like DOCX reconstruction."""

from enum import Enum
from pydantic import BaseModel, Field


class ZoneType(str, Enum):
    BODY = "body"
    HEADER = "header"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    MARGIN = "margin"


class ColumnZone(BaseModel):
    x0: float
    x1: float
    index: int = 0


class PageCanvas(BaseModel):
    """Stage 1 — page-level layout analysis."""

    page_num: int
    width: float
    height: float
    margin_left: float = 0.0
    margin_right: float = 0.0
    margin_top: float = 0.0
    margin_bottom: float = 0.0
    columns: list[ColumnZone] = Field(default_factory=list)
    column_count: int = 1


class VisualBlockKind(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list_item"
    TABLE = "table"
    IMAGE = "image"
    FOOTER = "footer"
    HEADER = "header"
    SIDEBAR = "sidebar"


class GridPlacement(BaseModel):
    """Block positioned on the virtual layout grid."""

    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    block_index: int
    is_spacer: bool = False
    spacer_height_pt: float = 0.0


class PageGrid(BaseModel):
    """Stage 5 — invisible layout grid for DOCX."""

    row_count: int
    col_count: int
    row_heights_pt: list[float] = Field(default_factory=list)
    col_widths_pt: list[float] = Field(default_factory=list)
    placements: list[GridPlacement] = Field(default_factory=list)
    row_boundaries: list[float] = Field(default_factory=list)
    col_boundaries: list[float] = Field(default_factory=list)


# PageLayout / DocumentModel live in app.pipeline.models (extended with canvas + grid).
