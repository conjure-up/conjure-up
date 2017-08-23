import asyncio

from conjureup import events
from conjureup.models.provider import LocalhostError, LocalhostJSONError


class BaseCloudController:
    retry_count = 0
    max_retry = 20

    async def _monitor_localhost(self, provider, cb):
        """ Checks that localhost/lxd is available and listening,
        updates widget accordingly
        """
        if events.LXDAvailable.is_set():
            return

        try:
            await provider.is_server_available()
            events.LXDAvailable.set()
            self.retry_count = 0
            cb()
        except (LocalhostError,
                LocalhostJSONError):
            if self.retry_count == self.max_retry:
                raise
            provider._set_lxd_dir_env()
            self.retry_count += 1
            await asyncio.sleep(2)
            await self._monitor_localhost(provider, cb)
        except FileNotFoundError:
            await asyncio.sleep(5)
            await self._monitor_localhost(provider, cb)
