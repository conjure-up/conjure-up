import asyncio
from pathlib import Path

from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.ui.views.interstitial import InterstitialView

from . import common


class BootstrapController(common.BaseBootstrapController):
    def __init__(self):
        self.bootstrapping = asyncio.Event()

    @property
    def msg_cb(self):
        return app.ui.set_footer

    def render(self):
        if app.is_jaas or self.is_existing_controller():
            bootstrap_stderr_path = None
            title = 'Creating Model'
            msg = 'Model'
        else:
            cache_dir = Path(app.config['spell-dir'])
            bootstrap_stderr_path = cache_dir / '{}-bootstrap.err'.format(
                app.provider.controller)
            title = 'Bootstrapping Controller'
            msg = 'Controller'

        self.bootstrapping.set()
        view = InterstitialView(
            title=title,
            message="Juju {} is initializing. Please wait.".format(msg),
            event=self.bootstrapping,
            watch_file=bootstrap_stderr_path)
        view.show()

        app.loop.create_task(self.run())
        app.loop.create_task(self.wait())

    async def wait(self):
        await events.Bootstrapped.wait()
        self.bootstrapping.clear()
        controllers.use('deploy').render()


_controller_class = BootstrapController
