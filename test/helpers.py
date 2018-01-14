import asyncio
import inspect
from contextlib import contextmanager
from unittest.mock import MagicMock, patch


@contextmanager
def test_loop():
    old_loop = asyncio.get_event_loop()
    new_loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(new_loop)
        with _patch_events(new_loop):
            yield new_loop
    finally:
        asyncio.set_event_loop(old_loop)
        new_loop.close()


@contextmanager
def _patch_events(new_loop):
    from conjureup import events
    patchers = []
    try:
        for name, obj in inspect.getmembers(events):
            if not isinstance(obj, asyncio.Event):
                continue
            patcher = patch.object(obj, '_loop', new_loop)
            patcher.start()
            patchers.append(patcher)
        yield
    finally:
        for patcher in patchers:
            patcher.stop()


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
