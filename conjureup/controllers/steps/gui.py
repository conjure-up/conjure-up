from conjureup.ui.views.steps import StepsView
from ubuntui.ev import EventLoop
from functools import partial
from conjureup import async
from conjureup.app_config import app
from conjureup import utils
from conjureup import controllers
from conjureup.models.step import StepModel
from . import common
import os.path as path
import os
import yaml
from collections import OrderedDict, deque
from conjureup.ui.widgets.step import StepWidget


class StepsController:
    def __init__(self):
        self.view = None
        self.bundle = path.join(
            app.config['spell-dir'], 'bundle.yaml')
        self.bundle_scripts = path.join(
            app.config['spell-dir'], 'conjure/steps'
        )
        self.steps = common.get_steps(self.bundle_scripts)

        self.results = OrderedDict()

    def __handle_exception(self, tag, exc):
        utils.pollinate(app.session_id, tag)
        EventLoop.remove_alarms()
        return app.ui.show_exception_message(exc)

    def get_result(self, future):
        try:
            step_model, step_widget = future.result()
            app.log.debug("Storing step result for: {}={}".format(
                step_model.title, step_model.result))
            self.results[step_model.title] = step_model.result

        except:
            return self.__handle_exception('E002', future.exception())

    def finish(self, step_model, step_widget, done=False):
        """ handles processing step with input data

        Arguments:
        step_model: step_model returned from widget
        done: if True continues on to the summary view
        """
        if done:
            return controllers.use('summary').render(self.results)

        # Set next button focus here now that the step is complete.
        self.view.steps.popleft()
        if len(self.view.steps) > 0:
            next_step = self.view.steps[0]
            next_step.generate_additional_input()
            self.view.step_pile.focus_position = self.view.step_pile.focus_position + 1  # noqa
        else:
            app.log.debug(
                "End of step list setting the view "
                "summary button in focus.")
            index = self.view.current_summary_button_index
            app.log.debug("Next focused button: {}".format(index))
            self.view.step_pile.focus_position = index

        future = async.submit(partial(common.do_step,
                                      step_model,
                                      step_widget,
                                      app.ui.set_footer,
                                      gui=True),
                              partial(self.__handle_exception, 'E002'))
        future.add_done_callback(self.get_result)

    def render(self):
        """ Render services status view
        """
        steps = deque()
        for step_path in self.steps:
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
                    self.finish)
                if not step_widget.model.viewable:
                    app.log.debug("Skipping step: {}".format(step_widget))
                    continue
                model.path = fname
                steps.append(step_widget)
                app.log.debug("Queueing step: {}".format(step_widget))
            except Exception as e:
                return self.__handle_exception('E002', e)

        try:
            self.view = StepsView(app, steps, self.finish)

            # Set initial step as active and viewable
            steps[0].description.set_text((
                'body', steps[0].model.description))
            steps[0].icon.set_text((
                'pending_icon', steps[0].icon.get_text()[0]
            ))
            steps[0].generate_additional_input()
            self.view.step_pile.focus_position = 2

        except Exception as e:
            return self.__handle_exception('E002', e)

        app.ui.set_header(
            title="Additional Application Configuration",
            excerpt="Please finish the installation by configuring your "
            "application with these steps.")
        app.ui.set_body(self.view)
        app.ui.set_footer('')


_controller_class = StepsController
