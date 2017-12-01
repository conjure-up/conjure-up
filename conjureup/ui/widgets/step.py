import asyncio

from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import submit_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import (
    IntegerEditor,
    PasswordEditor,
    SelectorHorizontal,
    StringEditor,
    YesNo
)
from urwid import Columns, Pile, Text, WidgetWrap

from conjureup import utils


class StepForm(WidgetWrap):
    INPUT_TYPES = {
        'text': StringEditor,
        'password': PasswordEditor,
        'boolean': YesNo,
        'integer': IntegerEditor,
        'choice': SelectorHorizontal
    }

    def __init__(self, app, step_model):
        """
        Arguments:
        step_model: step model
        step_model_widget: step model widget
        cb: callback
        """
        self.app = app
        self.model = step_model

        self.title = Text(('info_minor', step_model.title))
        self.description = Text(('body', step_model.description))
        self.result = Text(step_model.result)
        self.output = Text(('info_minor', ''))
        self.icon = Text(("pending_icon", "\N{BALLOT BOX}"))
        self.sudo_input = None
        self.complete = asyncio.Event()
        self.build_widget()
        self.build_fields()
        super().__init__(self.step_pile)

    def __repr__(self):
        return "<StepWidget: {}>".format(self.model.title)

    def set_output(self, msg):
        self.output.set_text(('info_context', msg))

    def clear_output(self):
        self.output.set_text("")

    def set_error(self, msg):
        self.output.set_text(('error_major', msg))

    def clear_error(self):
        self.clear_output()

    def set_icon_state(self, result_code):
        """ updates status icon

        Arguments:
        icon: icon widget
        result_code: 3 types of results, error, waiting, complete
        """
        if result_code == "error":
            self.icon.set_text(
                ("error_icon", "\N{BLACK FLAG}"))
        elif result_code == "waiting":
            self.icon.set_text(
                ("pending_icon", "\N{HOURGLASS}"))
        elif result_code == "active":
            self.icon.set_text(
                ("success_icon", "\N{BALLOT BOX WITH CHECK}"))
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            self.icon.set_text(("error_icon", "?"))

    @property
    def current_index(self):
        """ Returns the current pile index
        """
        return self.step_pile.focus_position

    @property
    def current_button_index(self):
        """ Returns the pile index where the button is located
        """
        return len(self.step_pile.contents) - 2

    def clear_button(self):
        """ Clears current button so it can't be pressed again
        """
        self.app.log.debug(
            "Contents: {}".format(
                self.step_pile.contents[self.current_button_index]))
        self.step_pile.contents[self.current_button_index] = (
            Text(""), self.step_pile.options())

    def show_button(self):
        self.step_pile.contents[self.current_button_index] = (
            Padding.right_20(
                Color.button_primary(self.button,
                                     focus_map='button_primary focus')),
            self.step_pile.options())

    def build_widget(self):
        self.step_pile = pile = Pile([
            self.description,
            Padding.line_break(""),
            Padding.push_4(self.output),
        ])

        if utils.is_linux() and self.model.needs_sudo:
            pile.contents.append((Padding.line_break(""), pile.options()))
            label = 'This step requires sudo.'
            if not self.app.sudo_pass:
                label += '  Enter sudo password, if needed:'
                self.sudo_input = PasswordEditor()
            columns = [
                ('weight', 0.5, Padding.left(Text(('body', label)), left=5)),
            ]
            if self.sudo_input:
                columns.append(('weight', 1, Color.string_input(
                    self.sudo_input, focus_map='string_input focus')))
            pile.contents.append((Columns(columns, dividechars=3),
                                  pile.options()))

    def build_fields(self):
        """ Generates widgets for additional input fields.
        """
        pile_opts = self.step_pile.options()
        self.fields = []
        for i in self.model.additional_input:
            label = i['label']
            key = i['key']
            if i['type'] not in self.INPUT_TYPES:
                self.app.log.error('Invalid input type "{}" in step {}; '
                                   'should be one of: {}'.format(
                                       i['type'],
                                       self.model.title,
                                       ', '.join(self.INPUT_TYPES.keys())))
                field = None
            else:
                input_type = self.INPUT_TYPES[i['type']]
                value = self.app.steps_data[self.model.name][key]
                if input_type == SelectorHorizontal:
                    select_w = input_type([choice for choice in i['choices']])
                    select_w.set_default(i['default'], True)
                    field = StepField(key, label, select_w, i['type'])
                else:
                    field = StepField(key, label,
                                      input_type(default=value), i['type'])
                self.fields.append(field)
            column_input = [
                ('weight', 0.5, Padding.left(field.label_widget, left=5))
            ]
            if field:
                column_input.append(
                    ('weight', 1, Color.string_input(
                        field.input, focus_map='string_input focus')))

            self.step_pile.contents.extend([
                (Padding.line_break(""), pile_opts),
                (Columns(column_input, dividechars=3), pile_opts),
            ])

        self.button = submit_btn(label="Next", on_press=self.submit)
        self.step_pile.contents.extend([
            (Padding.line_break(""), pile_opts),
            (Text(""), pile_opts),
            (HR(), pile_opts),
        ])

        if self.sudo_input or self.fields:
            self.show_button()
            self.step_pile.focus_position = 4
        else:
            self.complete.set()

    def lock_form(self):
        # make unselectable by "focusing" the non-focusable description
        self.step_pile.focus_position = 0
        self.clear_button()

    def submit(self, btn):
        self.app.loop.create_task(self.validate())

    async def validate(self):
        self.clear_button()
        has_error = False
        if self.sudo_input:
            self.set_output('Checking sudo...')
            if not await utils.can_sudo(self.sudo_input.value):
                self.set_error(
                    'Sudo failed.  Please check your password and ensure that '
                    'your sudo timeout is not set to zero.')
                has_error = True
            else:
                self.clear_output()
        for field in self.fields:
            if not field.input.value \
               and not field.input_type == 'boolean' \
               and self.model.required:
                field.label_widget.set_text(
                    ('error_major',
                     "{}: Missing required input.".format(field.label)))
                has_error = True
            else:
                field.label_widget.set_text(('body', field.label))
        if not has_error:
            self.set_icon_state('active')
            self.lock_form()
            self.complete.set()
        else:
            self.show_button()

    def keypress(self, size, key):
        if key == 'enter':
            if self.current_button_index in (self.current_index,
                                             self.current_index + 2):
                self.button.keypress(size, 'enter')
            else:
                self.step_pile.keypress(size, 'down')
        else:
            return super().keypress(size, key)


class StepField:
    def __init__(self, key, label, input, input_type):
        self.key = key
        self.label = label
        self.label_widget = Text(('body', label))
        self.input = input
        self.input_type = input_type


class StepResult(WidgetWrap):
    def __init__(self, step):
        self.step = step
        self.build_widget()
        return super().__init__(self.row)

    def build_widget(self):
        self.icon = Text(("pending_icon", "\N{BALLOT BOX}"))
        self.result = Text("")
        self.row = Columns([
            ('fixed', 3, self.icon),
            ('weight', 0.1, Text(('body', self.step.title))),
            ('weight', 0.4, self.result),
        ], dividechars=1)

    def mark_running(self):
        self.icon.set_text(("pending_icon", "\N{HOURGLASS}"))

    def mark_complete(self, result):
        self.icon.set_text(("success_icon", "\N{BALLOT BOX WITH CHECK}"))
        self.result.set_text(('body', result))
