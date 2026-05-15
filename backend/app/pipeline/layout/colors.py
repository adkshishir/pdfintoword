"""PDF color utilities (PyMuPDF / pdfplumber → hex for DOCX)."""


def int_to_rgb(color: int) -> tuple[int, int, int]:
    """PyMuPDF span color (sRGB int) → RGB 0–255."""
    if color < 0:
        color &= 0xFFFFFFFF
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def int_to_hex(color: int) -> str | None:
    if color is None:
        return None
    r, g, b = int_to_rgb(int(color))
    if (r, g, b) == (0, 0, 0):
        return None
    return rgb_to_hex(r, g, b)


def normalize_hex(hex_color: str | None) -> str | None:
    if not hex_color:
        return None
    h = hex_color.strip().lstrip("#").upper()
    if len(h) == 6:
        return f"#{h}"
    return None


def plumber_color_to_hex(color) -> str | None:
    if color is None:
        return None
    if isinstance(color, (list, tuple)) and len(color) >= 3:
        r, g, b = color[:3]
        if all(isinstance(v, float) and v <= 1.0 for v in (r, g, b)):
            return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))
        return rgb_to_hex(int(r), int(g), int(b))
    return None
