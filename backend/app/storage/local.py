import asyncio
import os
import shutil
from pathlib import Path

from app.config import get_settings


class LocalStorageBackend:
    def __init__(self) -> None:
        self.base_path = Path(get_settings().local_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _full_path(self, key: str) -> Path:
        full = self.base_path / key
        full.parent.mkdir(parents=True, exist_ok=True)
        return full

    async def put(self, key: str, data: bytes) -> None:
        path = self._full_path(key)

        def _write() -> None:
            path.write_bytes(data)

        await asyncio.to_thread(_write)

    async def get(self, key: str) -> bytes:
        path = self._full_path(key)

        def _read() -> bytes:
            if not path.exists():
                raise FileNotFoundError(key)
            return path.read_bytes()

        return await asyncio.to_thread(_read)

    async def delete(self, key: str) -> None:
        path = self._full_path(key)

        def _delete() -> None:
            if path.exists():
                path.unlink()

        await asyncio.to_thread(_delete)

    async def delete_prefix(self, prefix: str) -> None:
        target = self.base_path / prefix

        def _delete_prefix() -> None:
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()

        await asyncio.to_thread(_delete_prefix)
