import asyncio
from collections import OrderedDict, deque

from conjureup import controllers, events, utils
from conjureup.app_config import app
from conjureup.controllers.steps import common
from conjureup.telemetry import track_screen
from conjureup.ui.views.steps import StepsView
from conjureup.ui.widgets.step import StepWidget


class StepsController:

    def __init__(self):
        self.view = None
        self.step_metas = common.get_step_metadata_filenames()
        self.results = OrderedDict()
        self.step_queue = utils.IterQueue()

    def finish(self):
        return controllers.use('summary').render(self.results)

    def next_step(self, step_model, step_widget):
        """ handles processing step with input data

        Arguments:
        step_model: step_model returned from widget
        done: if True continues on to the summary view
        """

        if utils.is_linux() and step_model.needs_sudo:
            password = None
            if step_widget.sudo_input:
                password = step_widget.sudo_input.value
            if not utils.can_sudo(password):
                step_widget.set_error(
                    'Sudo failed.  Please check your password and ensure that '
                    'your sudo timeout is not set to zero.')
                step_widget.show_button()
                return

        step_widget.clear_error()
        step_widget.clear_button()
        step_widget.set_icon_state('waiting')

        # Set next button focus here now that the step is complete.
        self.view.steps.popleft()
        next_step = None
        if len(self.view.steps) > 0:
            next_step = self.view.steps[0]
            next_step.generate_additional_input()
            self.view.step_pile.focus_position = self.view.step_pile.focus_position + 1  # noqa

        # merge the step_widget input data into our step model
        for m in step_model.additional_input:
            try:
                matching_widget = next(filter(lambda i: i['key'] == m['key'],
                                              step_widget.additional_input))
                m['input'] = matching_widget['input'].value
            except StopIteration:
                app.log.error("Model field has no input: {}".format(m['key']))
                continue
        app.loop.create_task(self._put(step_model, step_widget, next_step))

    async def _put(self, step_model, step_widget, next_step):
        await self.step_queue.put((step_model, step_widget))
        if next_step is None:
            await self.step_queue.close()

    async def do_steps(self):
        async for step_model, step_widget in self.step_queue:
            result = await common.do_step(step_model, app.ui.set_footer)
            self.show_result(step_model, step_widget, result)

        events.PostDeployComplete.set()
        self.show_summary_button()

    def show_result(self, step_model, step_widget, result):
        self.results[step_model.title] = result
        step_widget.set_icon_state('active')
        step_widget.set_description(
            "{}\n\nResult: {}".format(
                step_model.description,
                result),
            'info_context')
        step_widget.show_output = False
        step_widget.clear_output()

    def show_summary_button(self):
        self.view.step_pile.contents.append(
            (self.view.buttons(),
             self.view.step_pile.options()))
        index = self.view.current_summary_button_index
        self.view.step_pile.focus_position = index

    async def refresh(self):
        while not events.PostDeployComplete.is_set():
            for w in self.all_step_widgets:
                w.update()
            await asyncio.sleep(1)

    def render(self):
        track_screen("Steps")
        if len(self.step_metas) == 0:
            self.finish()
            return

        step_widgets = deque()
        for step_meta_path in self.step_metas:
            # Store step model and its widget
            model = common.load_step(step_meta_path)
            if not model.viewable:
                app.log.debug("Skipping step: {}".format(model.title))
                continue
            step_widget = StepWidget(
                app,
                model,
                self.next_step)
            step_widgets.append(step_widget)
            app.log.debug("Queueing step: {}".format(step_widget))

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

        app.ui.set_header(
            title="Additional Application Configuration",
            excerpt="Please finish the installation by configuring your "
            "application with these steps.")
        app.ui.set_body(self.view)
        app.ui.set_footer('')
        app.loop.create_task(self.refresh())
        app.loop.create_task(self.do_steps())


_controller_class = StepsController
