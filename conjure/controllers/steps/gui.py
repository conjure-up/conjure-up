from conjure.ui.views.steps import StepsView
from ubuntui.ev import EventLoop
from functools import partial
from conjure import async
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from conjure.models.step import StepModel
from . import common
from glob import glob
import os.path as path
import os
import sys
import yaml
from collections import deque, OrderedDict


this = sys.modules[__name__]
this.view = None
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)
this.steps = deque(sorted(glob(
    os.path.join(this.bundle_scripts, 'step-*'))))

this.results = OrderedDict()


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    EventLoop.remove_alarms()
    return app.ui.show_exception_message(exc)


def get_result(future):
    try:
        result = future.result()
        app.log.debug("Storing step result for: {}={}".format(
            result.title, result.result))
        this.results[result.title] = result.result
    except:
        return __handle_exception('E002', future.exception())


def finish(step_model, done=False):
    """ handles processing step with input data

    Arguments:
    step_model: step_model returned from widget
    done: if True continues on to the summary view
    """
    if done:
        return controllers.use('summary').render(this.results)

    future = async.submit(partial(common.do_step,
                                  step_model,
                                  app.ui.set_footer,
                                  this.view.update_icon_state),
                          partial(__handle_exception, 'E002'))
    future.add_done_callback(get_result)


def render():
    """ Render services status view
    """
    steps = []
    for step_path in this.steps:
        fname, ext = path.splitext(step_path)
        step_metadata_path = "{}.yaml".format(fname)
        step_metadata = {}
        if path.isfile(step_metadata_path):
            with open(step_metadata_path) as fp:
                step_metadata = yaml.load(fp.read())
        model = StepModel(step_metadata)
        model.path = step_path
        steps.append(model)
        app.log.debug("Queueing step: {}".format(model))

    this.view = StepsView(app, steps, finish)

    app.ui.set_header(
        title="Additional Application Configuration")
    app.ui.set_body(this.view)
    app.ui.set_footer('')
