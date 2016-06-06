from conjure.ui.views.steps import StepsView
from ubuntui.ev import EventLoop
from functools import partial
from conjure import async
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from conjure.api.models import model_info
from . import common
from glob import glob
import os.path as path
import os
import json
import sys
from collections import deque


this = sys.modules[__name__]
this.view = None
this.post_exec_pollinate = False
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)
this.steps = deque(sorted(glob(os.path.join(this.bundle_scripts, '*.sh'))))
this.current_step = None
this.results = []


def finish():
    return controllers.use('summary').render(this.results)


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    app.ui.show_exception_message(exc)


def __handle_post_exception(exc):
    """ If an exception occurs in the post processing,
    log it but don't die
    """
    utils.pollinate(app.session_id, 'E002')
    app.log.exception(exc)


def __post_exec(*args):
    """ Executes a bundles post processing script if exists
    """

    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

    if not this.post_exec_pollinate:
        # We dont want to keep pollinating since this routine could
        # run multiple times
        utils.pollinate(app.session_id, 'XB')
        this.post_exec_pollinate = True

    # post step processing
    app.log.debug("Current steps: {}".format(this.steps))
    while this.steps:
        this.current_step = this.steps.popleft()
        if "00_pre.sh" in this.current_step \
           or "00_post-bootstrap.sh" in this.current_step \
           or "00_deploy-done.sh" in this.current_step:
            app.log.debug("Skipping non steps: {}".format(this.current_step))
            continue

        if os.access(this.current_step, os.X_OK):
            app.log.debug(
                "Running {}".format(this.current_step))
        future = async.submit(partial(common.run_script,
                                      this.current_step),
                              __handle_post_exception)
        future.add_done_callback(__post_exec_done)


def __post_exec_done(future):
    try:
        fr = future.result()
        try:
            result = json.loads(fr.stdout.decode())
        except json.decoder.JSONDecodeError:
            result = dict(returnCode=1, fr=fr,
                          jsonError=True,
                          message="Retrying post-processing.")

        app.log.debug("post_exec_done: {}".format(result))
        app.log.warning(fr.stderr.decode())

        this.view.update_step_message(this.current_step, result['message'])
        if result['returnCode'] > 0 or fr.returncode > 0:
            app.log.error(
                'There was an error during the post processing '
                'phase.')
            this.view.update_icon_state(this.current_step, 'error')
            EventLoop.remove_alarms()
        elif not result['isComplete']:
            this.steps.appendleft(this.current_step)
            this.view.update_icon_state(this.current_step, 'waiting')
            EventLoop.set_alarm_in(1, __post_exec)
        else:
            this.view.update_icon_state(this.current_step, 'active')
            this.results.append(result['message'])

            if not this.steps:
                EventLoop.remove_alarms()
                finish()
            EventLoop.set_alarm_in(1, __post_exec)
    except Exception as e:
        app.log.error(e)
        __handle_exception("E002", e)


def render():
    """ Render services status view
    """
    steps_dict = {}
    for step in this.steps:
        if "00_pre.sh" in step \
           or "00_post-bootstrap.sh" in step:
            continue
        steps_dict[step] = step
    this.view = StepsView(app, steps_dict)

    app.ui.set_header(
        title="Processing additional tasks")
    app.ui.set_body(this.view)
    app.ui.set_footer('')
    EventLoop.set_alarm_in(1, __post_exec)
