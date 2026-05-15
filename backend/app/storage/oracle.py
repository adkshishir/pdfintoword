import asyncio
import logging

from app.config import get_settings
from app.storage.local import LocalStorageBackend

logger = logging.getLogger(__name__)


class OracleStorageBackend:
    """Oracle Object Storage backend. Falls back to local when OCI is not configured."""

    def __init__(self) -> None:
        settings = get_settings()
        self._fallback = LocalStorageBackend()
        self._client = None
        if settings.oci_namespace and settings.oci_bucket_name and settings.oci_region:
            try:
                import oci

                config_kwargs = {}
                if settings.oci_config_file:
                    config_kwargs["file_location"] = settings.oci_config_file
                config = oci.config.from_file(**config_kwargs)
                self._client = oci.object_storage.ObjectStorageClient(config)
                self._namespace = settings.oci_namespace
                self._bucket = settings.oci_bucket_name
            except Exception as exc:
                logger.warning("OCI client init failed, using local fallback: %s", exc)

    async def put(self, key: str, data: bytes) -> None:
        if not self._client:
            await self._fallback.put(key, data)
            return

        def _put() -> None:
            self._client.put_object(self._namespace, self._bucket, key, data)

        await asyncio.to_thread(_put)

    async def get(self, key: str) -> bytes:
        if not self._client:
            return await self._fallback.get(key)

        def _get() -> bytes:
            response = self._client.get_object(self._namespace, self._bucket, key)
            return response.data.content

        return await asyncio.to_thread(_get)

    async def delete(self, key: str) -> None:
        if not self._client:
            await self._fallback.delete(key)
            return

        def _delete() -> None:
            self._client.delete_object(self._namespace, self._bucket, key)

        await asyncio.to_thread(_delete)

    async def delete_prefix(self, prefix: str) -> None:
        if not self._client:
            await self._fallback.delete_prefix(prefix)
            return

        def _delete_prefix() -> None:
            next_start = None
            while True:
                response = self._client.list_objects(
                    self._namespace,
                    self._bucket,
                    prefix=prefix,
                    start=next_start,
                )
                for obj in response.data.objects or []:
                    self._client.delete_object(self._namespace, self._bucket, obj.name)
                next_start = response.data.next_start_with
                if not next_start:
                    break

        await asyncio.to_thread(_delete_prefix)
