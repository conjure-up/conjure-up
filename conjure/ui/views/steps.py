from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)
from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import submit_btn, done_btn
from urwid import (WidgetWrap, Text, Filler, Pile, Columns,
                   SelectableIcon)


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

        self.additional_input = []
        if len(step_model.additional_input) > 0:
            for i in step_model.additional_input:
                widget = {
                    "label": Text(('info_minor', i['label'])),
                    "key": i['key'],
                    "input": self.INPUT_TYPES.get(i['type'])
                }
                if 'default' in i:
                    widget['input'] = StringEditor(default=i['default'])

                self.additional_input.append(widget)
        else:
            widget = {
                "label": Text(""),
                "key": "submit",
                "input": None
            }
            self.additional_input.append(widget)

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
        self.step_pile = Pile(self.build_steps())
        _pile = [
            Padding.center_90(HR()),
            Padding.line_break(""),
            Padding.center_90(self.step_pile),
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
        widgets = []
        for idx, step in enumerate(self.steps_queue):
            try:
                step.next_widget = self.steps_queue[idx+1].widget
            except IndexError:
                self.app.log.debug(
                    "No more next widgets, assuming end of steps list.")

            if not step.viewable:
                self.app.log.debug("{} is not viewable, skipping".format(
                    step))
                continue
            widgets.append(self.build_step(idx, step))
        return widgets

    def build_step(self, idx, step):

        # set first step title description color
        rows = []
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

        for i in step.widget.additional_input:
            self.app.log.debug(i)
            rows.append(Padding.line_break(""))
            column_input = [
                ('weight', 0.5, Padding.left(i['label'], left=5))
            ]
            if i['input']:
                column_input.append(
                    ('weight', 1, Color.string_input(
                        i['input'],
                        focus_map='string_input focus')))
            rows.append(Columns(column_input, dividechars=3))

            if idx == 0:
                label = "Submit"
            else:
                label = "Waiting for previous step to complete."

            rows.append(Padding.right_20(
                Color.button_primary(
                    submit_btn(
                        user_data=(idx, step),
                        on_press=self.submit,
                        label=label),
                    focus_map='button_primary focus')))
            rows.append(HR())

        return Pile(rows)

    def done(self, *args):
        self.cb({}, done=True)

    def submit(self, btn, idx_step_model):
        idx, step_model = idx_step_model

        if step_model.next_widget:
            next_button_text = "[ Go to next step ]"
        else:
            next_button_text = "[ Done ]"

        self.step_pile.contents[idx] = (
            Pile(
                [
                    Columns(
                        [
                            ('fixed', 3, step_model.widget.icon),
                            step_model.widget.description,
                        ], dividechars=1
                    ),
                    Padding.right_20(SelectableIcon(next_button_text)),
                    HR(),
                ]
            ),
            self.step_pile.options())

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
