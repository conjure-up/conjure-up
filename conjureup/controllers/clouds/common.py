import asyncio

from juju.utils import run_with_interrupt

from conjureup import events
from conjureup.models.provider import LocalhostError, LocalhostJSONError


class BaseCloudController:

    cancel_monitor = asyncio.Event()

    async def _monitor_localhost(self, provider, cb):
        """ Checks that localhost/lxd is available and listening,
        updates widget accordingly
        """

        while not self.cancel_monitor.is_set():
            try:
                compatible = await provider.is_server_compatible()
                if compatible:
                    events.LXDAvailable.set()
                    self.cancel_monitor.set()
                    cb()
                    return
            except (LocalhostError, LocalhostJSONError):
                provider._set_lxd_dir_env()
            except FileNotFoundError:
                pass
            await run_with_interrupt(asyncio.sleep(2),
                                     self.cancel_monitor)
