import asyncio
from contextlib import contextmanager
from unittest.mock import MagicMock


@contextmanager
def test_loop():
    old_loop = asyncio.get_event_loop()
    new_loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(new_loop)
        yield new_loop
    finally:
        asyncio.set_event_loop(old_loop)
        new_loop.close()


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
