from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field

from app.pipeline.canvas_models import PageCanvas, PageGrid


class BlockType(str, Enum):
    TEXT = "text"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    TABLE = "table"
    IMAGE = "image"


class BBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class TextSpan(BaseModel):
    text: str
    font_size: float = 12.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str | None = None
    font_name: str | None = None


class TextBlock(BaseModel):
    type: str = "text"
    text: str
    bbox: BBox
    spans: list[TextSpan] = Field(default_factory=list)
    font_size: float = 12.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str | None = None
    background_color: str | None = None
    font_name: str | None = None
    alignment: str = "left"
    level: int = 0
    is_header: bool = False
    is_footer: bool = False
    space_before_pt: float = 0.0
    left_indent_pt: float = 0.0


class TableCellStyle(BaseModel):
    text: str = ""
    background_color: str | None = None
    text_color: str | None = None
    bold: bool = False


class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    rows: list[list[str]]
    cell_styles: list[list[TableCellStyle]] | None = None
    bbox: BBox
    page_num: int = 0


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    data: bytes
    bbox: BBox
    width: int
    height: int
    page_num: int = 0


Block = Union[TextBlock, TableBlock, ImageBlock]


class PageLayout(BaseModel):
    page_num: int
    width: float
    height: float
    blocks: list[Block] = Field(default_factory=list)
    canvas: PageCanvas | None = None
    grid: PageGrid | None = None
    reading_order: list[int] = Field(default_factory=list)


class DocumentModel(BaseModel):
    pages: list[PageLayout] = Field(default_factory=list)
    pdf_type: str = "digital"
    ocr_used: bool = False
    use_visual_grid: bool = False

    model_config = {"arbitrary_types_allowed": True}
