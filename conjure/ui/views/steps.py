from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)
from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import submit_btn, done_btn
from urwid import (WidgetWrap, Text, Filler, Pile, Columns)


class StepWidget:
    INPUT_TYPES = {
        'text': StringEditor(),
        'password': PasswordEditor(),
        'boolean': YesNo(),
        'integer': IntegerEditor()
    }

    def __init__(self, step_model, cb):
        """

        Arguments:
        step_model: step model
        cb: submit button cb
        """
        self.title = Text(('info_minor', step_model.title))
        self.description = Text(('info_minor', step_model.description))
        self.result = Text(step_model.result)
        self.icon = Text(("pending_icon", "\N{BALLOT BOX}"))
        self.cb = cb
        self.idx = 0

        self.additional_input = []
        if len(step_model.additional_input) > 0:
            for i in step_model.additional_input:
                widget = {
                    "label": Text(('info_minor', i['label'])),
                    "key": i['key'],
                    "input": self.INPUT_TYPES.get(i['type']),
                    "submit": submit_btn(
                        user_data=step_model,
                        on_press=self.cb,
                        label="Waiting for previous step to complete.")
                }
                if 'default' in i:
                    widget['input'] = StringEditor(default=i['default'])

                self.additional_input.append(widget)
        self.submit = submit_btn(
            user_data=step_model,
            on_press=self.cb,
            label="Waiting for previous step to complete.")

        def __repr__(self):
            return "<Additional Input: {}".format(self.additional_input)


class StepsView(WidgetWrap):

    def __init__(self, app, steps, cb=None):
        """ init

        Arguments:
        cb: process step callback
        """
        self.app = app
        self.cb = cb
        self.steps_queue = [self.attach_step_widget_to_model(step)
                            for step in steps]
        _pile = [
            Padding.center_90(HR()),
            Padding.line_break(""),
            Padding.center_90(self.build_steps()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))

    def attach_step_widget_to_model(self, step_model):
        """ Attaches a step widget to step model
        """
        step_model.widget = StepWidget(step_model, self.submit)
        return step_model

    def buttons(self):
        buttons = [
            Color.button_primary(
                done_btn(on_press=self.done, label="View Summary"),
                focus_map='button_primary focus')
        ]
        return Pile(buttons)

    def build_steps(self):
        rows = []
        for idx, step in enumerate(self.steps_queue):
            step.widget.idx = idx
            try:
                step.next_widget = self.steps_queue[idx+1].widget
            except IndexError:
                self.app.log.debug("No more next widgets, skipping.")

            if not step.viewable:
                self.app.log.debug("{} is not viewable, skipping".format(
                    step))
                continue

            # set first step title description color
            if idx == 0:
                step.widget.description.set_text(('body', step.description))

            rows.append(
                Columns(
                    [
                        ('fixed', 3, step.widget.icon),
                        step.widget.description,
                    ], dividechars=1
                )
            )

            # Need to still prompt for the user to submit
            # even though no questions are asked
            if len(step.widget.additional_input) == 0:
                # set initial submit labels
                if idx == 0:
                    step.widget.submit.set_label(
                        "Submit")

                rows.append(
                    Padding.right_20(
                        Color.button_primary(
                            step.widget.submit,
                            focus_map='button_primary focus')))
                rows.append(HR())

            for i in step.widget.additional_input:
                self.app.log.debug(i)
                rows.append(Padding.line_break(""))
                rows.append(
                    Columns(
                        [
                            ('weight', 0.5, Padding.left(i['label'], left=5)),
                            ('weight', 1, Color.string_input(
                                i['input'],
                                focus_map='string_input focus')),
                        ], dividechars=3
                    )
                )

                if idx == 0:
                    i['submit'].set_label("Submit")
                rows.append(
                    Padding.right_20(
                        Color.button_primary(
                            i['submit'],
                            focus_map='button_primary focus')))
                rows.append(HR())

        return Pile(rows)

    def done(self, *args):
        self.cb({}, done=True)

    def submit(self, btn, step_model):
        btn.set_label('Submitted')
        # merge the step_widget input data into our step model
        for i in step_model.additional_input:
            try:
                matching_widget = [
                    x for x in step_model.widget.additional_input
                    if x['key'] == i['key']][0]
                i['input'] = matching_widget['input'].value
            except IndexError as e:
                self.app.log.error(
                    "Tried to pull a value from an "
                    "invalid input: {}/{}".format(e,
                                                  matching_widget))
        self.cb(step_model)
