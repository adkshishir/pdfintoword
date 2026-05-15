import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ConversionMode(str, enum.Enum):
    FAST = "fast"
    ACCURATE = "accurate"


class PdfType(str, enum.Enum):
    DIGITAL = "digital"
    SCANNED = "scanned"
    MIXED = "mixed"
