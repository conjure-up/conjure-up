import asyncio
from pathlib import Path

from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.telemetry import track_screen
from conjureup.ui.views.bootstrapwait import BootstrapWaitView

from . import common


class BootstrapController(common.BaseBootstrapController):
    @property
    def msg_cb(self):
        return app.ui.set_footer

    def render(self):
        track_screen("Bootstrap")

        if app.is_jaas or self.is_existing_controller():
            bootstrap_stderr_path = None
            msg = 'Model'
        else:
            cache_dir = Path(app.config['spell-dir'])
            bootstrap_stderr_path = cache_dir / '{}-bootstrap.err'.format(
                app.provider.controller)
            msg = 'Controller'

        view = BootstrapWaitView(
            app=app,
            message="Juju {} is initializing. Please wait.".format(msg),
            watch_file=bootstrap_stderr_path)
        app.ui.set_header(title="Waiting")
        app.ui.set_body(view)

        app.loop.create_task(self.run())
        app.loop.create_task(self.wait(view))

    async def wait(self, view):
        while not events.Bootstrapped.is_set():
            if events.Error.is_set():
                # bootstrap or add_model task failed, so stop refreshing
                # (the error screen will be shown instead)
                return
            view.redraw_kitt()
            await asyncio.sleep(1)
        controllers.use('deploy').render()


_controller_class = BootstrapController
