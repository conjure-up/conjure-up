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
from collections import OrderedDict, deque
from conjure.ui.widgets.step import StepWidget
from conjure.ui.widgets.stepmodel import StepModelWidget


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

    # Set next button focus here now that the step is complete.
    this.view.steps.popleft()
    if len(this.view.steps) > 0:
        next_step = this.view.steps[0]
        next_step.generate_additional_input()
        this.view.step_pile.focus_position = this.view.step_pile.focus_position + 1  # noqa
    else:
        app.log.debug(
            "End of step list setting the view "
            "summary button in focus.")
        index = this.view.current_summary_button_index
        app.log.debug("Next focused button: {}".format(index))
        this.view.step_pile.focus_position = index

    future = async.submit(partial(common.do_step,
                                  step_model,
                                  app.ui.set_footer,
                                  gui=True),
                          partial(__handle_exception, 'E002'))
    future.add_done_callback(get_result)


def render():
    """ Render services status view
    """
    steps = deque()
    for step_path in this.steps:
        fname, ext = path.splitext(step_path)
        if not path.isfile(fname) or not os.access(fname, os.X_OK):
            app.log.error(
                'Unable to process step, missing {}'.format(fname))
            continue
        step_metadata = {}
        with open(step_path) as fp:
            step_metadata = yaml.load(fp.read())

        try:
            # Store step model and its widget
            model = StepModel(step_metadata)
            step_widget = StepWidget(
                app,
                model,
                StepModelWidget(model),
                finish)
            if not step_widget.model.viewable:
                app.log.debug("Skipping step: {}".format(step_widget))
                continue
            model.path = fname
            steps.append(step_widget)
            app.log.debug("Queueing step: {}".format(step_widget))
        except Exception as e:
            return __handle_exception('E002', e)

    try:
        this.view = StepsView(app, steps, finish)

        # Set initial step as active and viewable
        steps[0].widget.description.set_text((
            'body', steps[0].model.description))
        steps[0].generate_additional_input()
        this.view.step_pile.focus_position = 2

    except Exception as e:
        return __handle_exception('E002', e)

    app.ui.set_header(
        title="Additional Application Configuration",
        excerpt="Please finish the installation by configuring your "
        "application with these steps.")
    app.ui.set_body(this.view)
    app.ui.set_footer('')
