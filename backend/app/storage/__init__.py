from app.config import get_settings
from app.storage.base import StorageBackend
from app.storage.local import LocalStorageBackend
from app.storage.oracle import OracleStorageBackend


def get_storage() -> StorageBackend:
    backend = get_settings().storage_backend.lower()
    if backend == "oracle":
        return OracleStorageBackend()
    return LocalStorageBackend()
