from conjure.ui.views.steps import StepsView
from ubuntui.ev import EventLoop
from functools import partial
from conjure import async
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from . import common
from glob import glob
import os.path as path
import os
import sys
from collections import deque


this = sys.modules[__name__]
this.view = None
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)
this.steps = deque(sorted(glob(os.path.join(this.bundle_scripts, '*.sh'))))


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    EventLoop.remove_alarms()
    return app.ui.show_exception_message(exc)


def __fatal(error):
    """ If an exception occurs in the post processing,
    log it and die
    """
    app.log.exception(Exception(error))
    return __handle_exception('E002', Exception(error))


def __post_exec(*args):
    """ Executes a bundles post processing script if exists
    """
    # post step processing
    future = async.submit(partial(common.wait_for_steps,
                                  this.steps,
                                  app.ui.set_footer,
                                  this.view.update_icon_state),
                          partial(__handle_exception, 'E002'))
    future.add_done_callback(finish)


def finish(future):
    try:
        results = future.result()
    except:
        return __handle_exception('E002', future.exception())
    return controllers.use('summary').render(results)


def render():
    """ Render services status view
    """
    steps_dict = {}
    for step in this.steps:
        if "00_pre.sh" in step \
           or "00_post-bootstrap.sh" in step \
           or "00_deploy-done.sh" in step:
            continue
        steps_dict[step] = step
    this.view = StepsView(app, steps_dict)

    app.ui.set_header(
        title="Processing additional tasks")
    app.ui.set_body(this.view)
    app.ui.set_footer('')
    __post_exec()
