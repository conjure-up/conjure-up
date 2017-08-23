import asyncio

from conjureup import events, utils
from conjureup.app_config import app
from conjureup.models.provider import LocalhostError, LocalhostJSONError


class BaseCloudController:
    retry_count = 0
    max_retry = 20

    async def _monitor_localhost(self, cb):
        """ Checks that localhost/lxd is available and listening,
        updates widget accordingly
        """
        if events.LXDAvailable.is_set():
            return

        try:
            await app.provider.is_server_available()
            events.LXDAvailable.set()
            self.retry_count = 0
            cb()
        except (LocalhostError,
                LocalhostJSONError):
            if self.retry_count == self.max_retry:
                raise
            app.provider._set_lxd_dir_env()
            self.retry_count += 1
            await asyncio.sleep(2)
            await self._monitor_localhost(cb)
        except FileNotFoundError:
            if app.headless:
                utils.error("Unable to find lxc executable, please make "
                            "sure LXD is installed: `sudo snap install lxd`")
                events.Shutdown.set(1)
            await asyncio.sleep(5)
            await self._monitor_localhost(cb)
