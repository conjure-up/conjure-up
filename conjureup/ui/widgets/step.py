import asyncio

from ubuntui.utils import Color, Padding
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import (
    IntegerEditor,
    PasswordEditor,
    StringEditor,
    YesNo
)
from urwid import Columns, Filler, Pile, Text, WidgetWrap

from conjureup import utils
from conjureup.ui.widgets.buttons import SubmitButton
from conjureup.ui.widgets.selectors import (
    RadioList,
    ValuedCheckBox,
    ValuedRadioButton,
)


class StepForm(Pile):
    INPUT_TYPES = {
        'text': StringEditor,
        'password': PasswordEditor,
        'boolean': YesNo,
        'integer': IntegerEditor,
        'choice': RadioList,
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
        self.sudo_label = Text(('body', ''))
        self.icon = Text(("pending_icon", "\N{BALLOT BOX}"))
        self.sudo_input = None
        self.complete = asyncio.Event()
        self.requires_input = False
        form_fields = (self._build_form_header() +
                       self._build_sudo_field() +
                       self._build_form_fields())
        super().__init__(form_fields)
        if self.sudo_input or self.fields:
            self.show_button()
            self.focus_position = 4

    def __repr__(self):
        return "<StepForm: {} ()>".format(self.model.title, self.selectable())

    def set_sudo_label(self, msg):
        self.sudo_label.set_text(('info_context', msg))

    def clear_sudo_error(self):
        label = 'This step requires sudo.'
        if not self.app.sudo_pass:
            label += '  Enter sudo password, if needed:'
        self.sudo_label.set_text(label)

    def set_sudo_error(self, msg):
        self.sudo_label.set_text(('error_major', msg))

    def clear_error(self):
        self.clear_sudo_error()

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
    def current_button_index(self):
        """ Returns the pile index where the button is located
        """
        return len(self.contents) - 2

    def clear_button(self):
        """ Clears current button so it can't be pressed again
        """
        self.contents[self.current_button_index] = (Text(""), self.options())

    def show_button(self, label=None, disabled=False):
        self.button.set_label(label or 'Next')
        if disabled:
            self.button.on_press = lambda btn: None
            button = self.button
        else:
            self.button.on_press = self.submit
            button = Color.button_primary(self.button,
                                          focus_map='button_primary focus')
        self.contents[self.current_button_index] = (Padding.right_20(button),
                                                    self.options())

    def append(self, widget):
        self.contents.append((widget, self.options()))

    def extend(self, widgets):
        for widget in widgets:
            self.append(widget)

    def _build_form_header(self):
        return [
            self.description,
            Padding.line_break(""),
            HR(),
        ]

    def _build_sudo_field(self):
        if not utils.is_linux() or not self.model.needs_sudo:
            return []

        rows = []
        if not self.app.sudo_pass:
            self.sudo_input = PasswordEditor()
        self.clear_sudo_error()
        columns = [
            ('weight', 0.5, Padding.left(self.sudo_label, left=5)),
        ]
        if self.sudo_input:
            columns.append((
                'weight', 1,
                Filler(Color.string_input(self.sudo_input,
                                          focus_map='string_input focus'),
                       valign='bottom')))
        rows.extend([
            Padding.line_break(""),
            Columns(columns, dividechars=3, box_columns=[1]),
        ])
        return rows

    def _build_form_fields(self):
        """ Generates widgets for additional input fields.
        """
        form_fields = []
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
                if issubclass(input_type, RadioList):
                    select_w = input_type([choice for choice in i['choices']])
                    select_w.select_option(i['default'])
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

            form_fields.extend([
                Padding.line_break(""),
                Columns(column_input, dividechars=3),
            ])

        self.button = SubmitButton(label="Next", on_press=self.submit)
        self.requires_input = self.sudo_input or self.fields
        form_fields.extend([
            Padding.line_break(""),
            self.button if self.requires_input else Text(""),
            HR(),
        ])

        if self.requires_input:
            self.complete.clear()
        else:
            self.complete.set()

        return form_fields

    def lock_form(self):
        # make unselectable by "focusing" the non-focusable description
        self.focus_position = 0
        self.clear_button()

    def submit(self, btn):
        self.app.loop.create_task(self.validate())

    async def validate(self):
        error_field = None
        if self.sudo_input:
            self.clear_sudo_error()
            # the sudo form can be at the bottom of a long list of forms and
            # if there is no focused widget below it, it will get scrolled
            # off the bottom while checking, making it invisible; so we render
            # the button disabled and focus it to ensure the user can see the
            # sudo form
            self.show_button('Checking sudo...', disabled=True)
            self.focus_position = self.current_button_index
            if not await utils.can_sudo(self.sudo_input.value):
                self.set_sudo_error(
                    'Sudo failed.  Please check your password and ensure that '
                    'your sudo timeout is not set to zero.')
                error_field = self.sudo_input
            else:
                self.clear_sudo_error()
        self.clear_button()
        for field in self.fields:
            missing = False
            if field.input_type != 'boolean' and \
                    not field.input.value and \
                    self.model.required:
                missing = True
            elif field.input_type == 'boolean' and \
                    field.input.value is None and \
                    self.model.required:
                missing = True
            if missing:
                field.label_widget.set_text(
                    ('error_major',
                     "{}: Missing required input.".format(field.label)))
                if error_field is None:
                    error_field = field.input
            else:
                field.label_widget.set_text(('body', field.label))
        if not error_field:
            self.set_icon_state('active')
            self.lock_form()
            self.complete.set()
        else:
            self.show_button()
            # find the first field that errored and select it
            orig_focus_position = self.focus_position
            for i in range(len(self.contents)):
                self.focus_position = i
                focus_field = self.get_focus_widgets()[-1].base_widget
                if isinstance(focus_field, (ValuedCheckBox,
                                            ValuedRadioButton)):
                    # compare the whole list, not individual item
                    focus_field = self.get_focus_widgets()[-2].base_widget
                if focus_field is error_field:
                    break
            else:
                # field not found??  restore focus_position
                self.focus_position = orig_focus_position


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
