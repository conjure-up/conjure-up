import os.path as path
from collections import OrderedDict, deque
from functools import partial

from ubuntui.ev import EventLoop

from conjureup import async, controllers, utils
from conjureup.app_config import app
from conjureup.controllers.steps import common
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.steps import StepsView
from conjureup.ui.widgets.step import StepWidget


class StepsController:

    def __init__(self):
        self.view = None
        self.bundle_scripts = path.join(
            app.config['spell-dir'], 'steps'
        )
        self.step_metas = common.get_step_metadata_filenames(
            self.bundle_scripts)

        self.results = OrderedDict()

    def __handle_exception(self, tag, exc):
        track_exception(exc.args[0], is_fatal=True)
        EventLoop.remove_alarms()
        app.ui.show_exception_message(exc)

    def get_result(self, future):
        if future.exception():
            self.__handle_exception('E002', future.exception())
            return

        step_model, step_widget = future.result()

        step_widget.set_icon_state('active')
        step_widget.set_description(
            "{}\n\nResult: {}".format(
                step_model.description,
                step_model.result),
            'info_context')
        step_widget.show_output = False
        step_widget.clear_output()

        app.log.debug("Storing step result for: {}={}".format(
            step_model.title, step_model.result))
        self.results[step_model.title] = step_model.result
        self.n_completed_steps += 1
        if self.n_completed_steps == len(self.all_step_widgets):
            app.log.debug(
                "End of step list waiting for last step to complete "
                "then rendering summary.")

            self.view.step_pile.contents.append(
                (self.view.buttons(),
                 self.view.step_pile.options()))
            index = self.view.current_summary_button_index
            self.view.step_pile.focus_position = index

    def finish(self, step_model, step_widget, done=False):
        """ handles processing step with input data

        Arguments:
        step_model: step_model returned from widget
        done: if True continues on to the summary view
        """
        if done:
            EventLoop.remove_alarms()
            return controllers.use('summary').render(self.results)

        if utils.is_linux() and step_model.needs_sudo:
            password = None
            if step_widget.sudo_input:
                password = step_widget.sudo_input.value
            if not step_model.can_sudo(password):
                step_widget.set_error(
                    'Sudo failed.  Please check your password and ensure that '
                    'your sudo timeout is not set to zero.')
                step_widget.show_button()
                return

        step_widget.clear_error()

        # Set next button focus here now that the step is complete.
        self.view.steps.popleft()

        if len(self.view.steps) > 0:
            next_step = self.view.steps[0]
            next_step.generate_additional_input()
            self.view.step_pile.focus_position = self.view.step_pile.focus_position + 1  # noqa

        future = async.submit(partial(common.do_step,
                                      step_model,
                                      step_widget,
                                      app.ui.set_footer,
                                      gui=True),
                              partial(self.__handle_exception, 'E002'))
        if future:
            future.add_done_callback(self.get_result)

    def update(self, *args):
        for w in self.all_step_widgets:
            w.update()
        EventLoop.set_alarm_in(1, self.update)

    def render(self):
        track_screen("Steps")
        if len(self.step_metas) == 0:
            self.finish(None, None, done=True)
            return

        step_widgets = deque()
        self.n_completed_steps = 0
        for step_meta_path in self.step_metas:
            try:
                # Store step model and its widget
                model = common.load_step(step_meta_path)
                if not model.viewable:
                    app.log.debug("Skipping step: {}".format(model.title))
                    continue
                step_widget = StepWidget(
                    app,
                    model,
                    self.finish)
                step_widgets.append(step_widget)
                app.log.debug("Queueing step: {}".format(step_widget))
            except Exception as e:
                app.log.exception(e)
                self.__handle_exception('E002', e)
                return

        try:
            self.all_step_widgets = list(step_widgets)
            self.view = StepsView(app, step_widgets, self.finish)

            # Set initial step as active and viewable
            step_widgets[0].description.set_text((
                'body', step_widgets[0].model.description))
            step_widgets[0].icon.set_text((
                'pending_icon', step_widgets[0].icon.get_text()[0]
            ))
            step_widgets[0].generate_additional_input()
            self.view.step_pile.focus_position = 2

        except Exception as e:
            self.__handle_exception('E002', e)
            return

        app.ui.set_header(
            title="Additional Application Configuration",
            excerpt="Please finish the installation by configuring your "
            "application with these steps.")
        app.ui.set_body(self.view)
        app.ui.set_footer('')
        self.update()


_controller_class = StepsController
