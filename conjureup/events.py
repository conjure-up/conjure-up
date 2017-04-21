import asyncio
from collections import defaultdict

from ubuntui.ev import EventLoop
from urwid import ExitMainLoop

from conjureup import utils
from conjureup.app_config import app
from conjureup.telemetry import track_exception


class Event(asyncio.Event):
    def __init__(self, name):
        self._name = name
        super().__init__()

    def set(self):
        app.log.debug('Setting {}'.format(self._name))
        super().set()

    def clear(self):
        app.log.debug('Clearing {}'.format(self._name))
        super().clear()


class NamedEvent:
    """
    Event wrapper that manages individual events per name.
    """

    def __init__(self, name):
        self._name = name
        self._events = defaultdict(asyncio.Event)

    def set(self, name):
        app.log.debug('Setting {}:{}'.format(self._name, name))
        self._events[name].set()

    def clear(self, name):
        app.log.debug('Clearing {}:{}'.format(self._name, name))
        self._events[name].clear()

    def is_set(self, name):
        return self._events[name].is_set()

    async def wait(self, name):
        return await self._events[name].wait()


class ShutdownEvent(Event):
    def set(self, exit_code=None):
        if exit_code is not None:
            app.exit_code = exit_code
        return super().set()


Error = Event('Error')
Shutdown = ShutdownEvent('Shutdown')
MAASConnected = Event('MAASConnected')
Bootstrapped = Event('Bootstrapped')
ModelAvailable = Event('ModelAvailable')
ModelConnected = Event('ModelConnected')
PreDeployComplete = Event('PreDeployComplete')
MachinesCreated = NamedEvent('MachinesCreated')
AppDeployed = NamedEvent('AppDeployed')
PendingRelations = NamedEvent('PendingRelations')
RelationsAdded = NamedEvent('RelationsAdded')
DeploymentComplete = Event('DeploymentComplete')
ModelSettled = Event('ModelSettled')
PostDeployComplete = Event('PostDeployComplete')


def unhandled_input(key):
    if key in ['q', 'Q']:
        Shutdown.set()
    if key in ['R']:
        EventLoop.redraw_screen()


def handle_exception(loop, context):
    if 'exception' not in context:
        return  # not an error, cleanup message
    if isinstance(context['exception'], ExitMainLoop):
        Shutdown.set()  # use previously stored exit code
        return
    if Error.is_set():
        return  # already reporting an error
    Error.set()
    exc = context['exception']
    track_exception(str(exc))

    # not sure of a cleaner way to log the exception instance
    try:
        raise exc
    except type(exc):
        app.log.exception('Unhandled exception')

    if app.headless:
        utils.error(exc)
        Shutdown.set(1)
    else:
        app.exit_code = 1  # store exit code for later
        app.ui.show_exception_message(exc)  # eventually raises ExitMainLoop


async def shutdown_watcher():
    app.log.info('Watching for shutdown')
    try:
        await Shutdown.wait()
    except asyncio.CancelledError:
        pass

    app.log.info('Shutting down')
    if app.headless:
        utils.warning('Shutting down')
    else:
        app.ui.show_shutdown_message()

    try:
        if app.juju.authenticated:
            app.log.info('Disconnecting model')
            await app.juju.client.disconnect()
            app.log.info('Disconnected')

        if not app.headless:
            EventLoop.remove_alarms()

        for task in asyncio.Task.all_tasks(app.loop):
            # cancel all other tasks
            if getattr(task, '_coro', None) is not shutdown_watcher:
                task.cancel()
        app.loop.stop()
    except Exception:
        app.log.exception('Error in cleanup code')
        raise
