import asyncio
import errno
import inspect
from pathlib import Path

from ubuntui.ev import EventLoop
from urwid import ExitMainLoop

from conjureup import utils
from conjureup.app_config import app
from conjureup.controllers.lxdsetup.common import LXDInvalidUserError
from conjureup.telemetry import track_exception


class Event(asyncio.Event):
    def __init__(self, name):
        self._name = name
        super().__init__()

    def _log(self, action):
        base_path = Path(__file__).parent.parent
        frame = inspect.stack()[2]
        event_methods = ('set', 'clear', 'wait')
        if frame.filename == __file__ and frame.function in event_methods:
            # NamedEvent wraps these methods and we want the original
            # caller, so we need to jump up an extra stack frame
            frame = inspect.stack()[3]
        task = getattr(asyncio.Task.current_task(), '_coro', '')
        try:
            frame_file = Path(frame.filename).relative_to(base_path)
        except ValueError:
            frame_file = Path(frame.filename)
        frame_lineno = frame.lineno
        if task:
            code = task.cr_frame.f_code
            task_name = code.co_name
            try:
                task_file = Path(code.co_filename).relative_to(base_path)
            except ValueError:
                task_file = Path(code.co_filename)
            task_lineno = task.cr_frame.f_lineno
            if task_file != frame_file or task_lineno != frame_lineno:
                task = ' in task {} at {}:{}'.format(task_name,
                                                     task_file,
                                                     task_lineno)
            else:
                task = ''
        app.log.debug('{} {} at {}:{}{}'.format(action,
                                                self._name,
                                                frame_file,
                                                frame_lineno,
                                                task))

    def set(self):
        self._log('Setting')
        super().set()

    def clear(self):
        self._log('Clearing')
        super().clear()

    async def wait(self):
        self._log('Awaiting')
        await super().wait()
        self._log('Received')


class NamedEvent:
    """
    Event wrapper that manages individual events per name.
    """

    def __init__(self, name):
        self._name = name
        self._events = {}

    def _event(self, name):
        if name not in self._events:
            self._events[name] = Event(':'.join([self._name, name]))
        return self._events[name]

    def set(self, name):
        self._event(name).set()

    def clear(self, name):
        self._event(name).clear()

    def is_set(self, name):
        return self._event(name).is_set()

    async def wait(self, name):
        return await self._event(name).wait()


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
MachinePending = NamedEvent('MachinePending')
MachineCreated = NamedEvent('MachineCreated')
AppMachinesCreated = NamedEvent('AppMachinesCreated')
AppDeployed = NamedEvent('AppDeployed')
PendingRelations = NamedEvent('PendingRelations')
RelationsAdded = NamedEvent('RelationsAdded')
DeploymentComplete = Event('DeploymentComplete')
ModelSettled = Event('ModelSettled')
PostDeployComplete = Event('PostDeployComplete')


# Keep a list of exceptions we know that shouldn't be logged
# into sentry.
NOTRACK_EXCEPTIONS = [
    lambda exc: exc is OSError and exc.errno == errno.ENOSPC,
    lambda exc: isinstance(exc, LXDInvalidUserError)
]


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
    if not app.noreport or any(pred(exc) for pred in NOTRACK_EXCEPTIONS):
        try:
            exc_info = (type(exc), exc, exc.__traceback__)
            app.sentry.captureException(exc_info, tags={
                'spell': app.config.get('spell'),
                'cloud_type': app.current_cloud_type,
                'region': app.current_region,
                'jaas': app.is_jaas,
                'headless': app.headless,
                'juju_version': utils.juju_version(),
                'lxd_version': utils.lxd_version(),
            })
        except Exception:
            app.log.exception('Error reporting error')

    app.log.exception('Unhandled exception', exc_info=exc)

    if app.headless:
        msg = str(exc)
        utils.error(msg)
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
