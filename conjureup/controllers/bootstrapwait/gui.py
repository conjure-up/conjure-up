import asyncio
from pathlib import Path

from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.telemetry import track_screen
from conjureup.ui.views.bootstrapwait import BootstrapWaitView


class BootstrapWaitController:
    def render(self):
        if events.Bootstrapped.is_set():
            return controllers.use('deploy').render()
        track_screen("Bootstrap wait")
        app.log.debug("Rendering bootstrap wait")

        if app.is_jaas:
            bootstrap_stderr_path = None
        else:
            cache_dir = Path(app.config['spell-dir'])
            bootstrap_stderr_path = cache_dir / '{}-bootstrap.err'.format(
                app.current_controller)
        view = BootstrapWaitView(
            app=app,
            message="Juju Controller is initializing. Please wait.",
            watch_file=bootstrap_stderr_path)
        app.ui.set_header(title="Waiting")
        app.ui.set_body(view)

        app.loop.create_task(self.refresh(view))
        app.loop.create_task(self.finish())

    async def refresh(self, view):
        while not events.Bootstrapped.is_set():
            view.redraw_kitt()
            await asyncio.sleep(1)

    async def finish(self):
        await events.Bootstrapped.wait()
        return controllers.use('deploy').render()


_controller_class = BootstrapWaitController
