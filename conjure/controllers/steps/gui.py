from conjure.ui.views.steps import StepsView
from ubuntui.ev import EventLoop
from functools import partial
from conjure import async
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from conjure.models.step import StepModel
from . import common
import os.path as path
import os
import sys
import yaml
from collections import OrderedDict


this = sys.modules[__name__]
this.view = None
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)
this.steps = common.get_steps(this.bundle_scripts)

this.results = OrderedDict()


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    EventLoop.remove_alarms()
    return app.ui.show_exception_message(exc)


def get_result(future):
    try:
        result = future.result()
        app.log.debug("Storing step result for: {}={}".format(
            result.model.title, result.model.result))
        this.results[result.model.title] = result.model.result
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
                                  gui=True),
                          partial(__handle_exception, 'E002'))
    future.add_done_callback(get_result)


def render():
    """ Render services status view
    """
    steps = []
    for step_path in this.steps:
        fname, ext = path.splitext(step_path)
        if not path.isfile(fname) or not os.access(fname, os.X_OK):
            app.log.error(
                'Unable to process step, missing {}'.format(fname))
            continue
        step_metadata = {}
        with open(step_path) as fp:
            step_metadata = yaml.load(fp.read())
        model = StepModel(step_metadata)
        model.path = fname
        steps.append(model)
        app.log.debug("Queueing step: {}".format(model))

    try:
        this.view = StepsView(app, steps, finish)

        # Set initial step as active and viewable
        steps[0].widget.description.set_text((
            'body', steps[0].description))

    except Exception as e:
        return __handle_exception('E002', e)

    app.ui.set_header(
        title="Additional Application Configuration",
        excerpt="Please finish the installation by configuring your "
        "application with these steps.")
    app.ui.set_body(this.view)
    app.ui.set_footer('')
