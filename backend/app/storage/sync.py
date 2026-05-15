from app.storage import get_storage


def storage_get_sync(key: str) -> bytes:
    import asyncio

    storage = get_storage()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(storage.get(key))


def storage_put_sync(key: str, data: bytes) -> None:
    import asyncio

    storage = get_storage()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(storage.put(key, data))
