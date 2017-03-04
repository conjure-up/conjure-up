from asyncio import CancelledError, Event, Task
from collections import defaultdict

from ubuntui.ev import EventLoop
from urwid import ExitMainLoop

from conjureup import utils
from conjureup.app_config import app
from conjureup.telemetry import track_exception


class ShutdownEvent(Event):
    def set(self, exit_code=None):
        if exit_code is not None:
            app.exit_code = exit_code
        return super().set()


class NamedEvent:
    """
    Event wrapper that manages individual events per name.
    """

    def __init__(self):
        self._events = defaultdict(Event)

    def set(self, name):
        self._events[name].set()

    def clear(self, name):
        self._events[name].clear()

    def is_set(self, name):
        return self._events[name].is_set()

    async def wait(self, name):
        return await self._events[name].wait()


Error = Event()
Shutdown = ShutdownEvent()
MAASConnected = Event()
Bootstrapped = Event()
ModelAvailable = Event()
ModelConnected = Event()
PreDeployComplete = Event()
MachinesCreated = NamedEvent()
AppDeployed = NamedEvent()
PendingRelations = NamedEvent()
RelationsAdded = NamedEvent()
ModelSettled = Event()
PostDeployComplete = Event()


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
    track_exception(exc.args[0])

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
    except CancelledError:
        pass

    app.log.info('Shutting down')
    if app.headless:
        utils.warning('Shutting down')

    try:
        if app.juju.authenticated:
            app.log.info('Disconnecting model')
            await app.juju.client.disconnect()
            app.log.info('Disconnected')

        if not app.headless:
            EventLoop.remove_alarms()

        for task in Task.all_tasks(app.loop):
            # cancel all other tasks
            if getattr(task, '_coro', None) is not shutdown_watcher:
                task.cancel()
        app.loop.stop()
    except Exception:
        app.log.exception('Error in cleanup code')
        raise
