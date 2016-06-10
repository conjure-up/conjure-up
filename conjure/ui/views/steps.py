from conjure.ui.widgets.step import StepWidget
from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)
from ubuntui.utils import Padding, Color
from ubuntui.widgets.table import Table
from ubuntui.widgets.buttons import submit_btn, done_btn
from urwid import WidgetWrap, Text
import random


class StepsView(WidgetWrap):

    INPUT_TYPES = {
        'text': StringEditor(),
        'password': PasswordEditor(),
        'boolean': YesNo(),
        'integer': IntegerEditor()
    }

    def __init__(self, app, steps, cb=None):
        """ init

        Arguments:
        cb: process step callback
        """
        self.app = app
        self.table = Table()
        self.cb = cb

        self.steps_queue = steps
        for step_model in self.steps_queue:
            step_widget = self.add_step_widget(step_model)
            self.table.addColumns(
                step_model.path,
                [
                    ('fixed', 3, step_widget['icon']),
                    step_widget['description'],
                ]
            )
            # Need to still prompt for the user to submit
            # even though no questions are asked
            if len(step_widget['additional_input']) == 0:
                self.table.addRow(
                    Padding.right_20(
                        Color.button_primary(
                            submit_btn(on_press=self.submit,
                                       user_data=(step_model, step_widget)),
                            focus_map='button_primary focus')), False)
            for i in step_widget['additional_input']:
                self.table.addRow(Padding.line_break(""), False)
                self.table.addColumns(
                    step_model.path,
                    [
                        ('weight', 0.5, Padding.left(i['label'], left=5)),
                        ('weight', 1, Color.string_input(
                            i['input'],
                            focus_map='string_input focus')),
                    ], force=True
                )
                self.table.addRow(
                    Padding.right_20(
                        Color.button_primary(
                            submit_btn(
                                on_press=self.submit,
                                user_data=(step_model, step_widget)),
                            focus_map='button_primary focus')), False)
                self.table.addRow(Padding.line_break(""), False)

        self.table.addRow(Padding.center_20(
                        Color.button_primary(
                            done_btn(on_press=self.done, label="View Summary"),
                            focus_map='button_primary focus')))
        super().__init__(Padding.center_80(self.table.render()))

    def add_step_widget(self, step_model):
        if not step_model.viewable:
            return

        step_widget_dict = {'title': Text(step_model.title),
                            'description': Text(step_model.description),
                            'result': Text(step_model.result),
                            'icon': Text(step_model.icon)}
        step_widget_dict['additional_input'] = []
        if len(step_model.additional_input) > 0:
            for i in step_model.additional_input:
                widget = {
                    "label": Text(i['label']),
                    "key": i['key'],
                    "input": self.INPUT_TYPES.get(i['type'])
                }
                if 'default' in i:
                    widget['input'] = StringEditor(default=i['default'])

                step_widget_dict['additional_input'].append(widget)
        return step_widget_dict

    def done(self, *args):
        self.cb({}, done=True)

    def submit(self, btn, stepmodel_stepwidget):
        step_model, step_widget = stepmodel_stepwidget

        # set icon
        step_model.icon = step_widget['icon']
        # merge the step_widget input data into our step model
        for i in step_model.additional_input:
            try:
                matching_widget = [x for x in step_widget['additional_input']
                                   if x['key'] == i['key']][0]
                i['input'] = matching_widget['input'].value
            except IndexError as e:
                self.app.log.error(
                    "Tried to pull a value from an "
                    "invalid input: {}/{}".format(e,
                                                  matching_widget))
        self.cb(step_model)

    def update_icon_state(self, icon, result_code):
        """ updates status icon

        Arguments:
        icon: icon widget
        result_code: 3 types of results, error, waiting, complete
        """
        if result_code == "error":
            icon.set_text(
                ("error_icon", "\N{BLACK FLAG}"))
        elif result_code == "waiting":
            pending_status = [("pending_icon", "\N{CIRCLED BULLET}"),
                              ("pending_icon", "\N{CIRCLED WHITE BULLET}"),
                              ("pending_icon", "\N{FISHEYE}")]
            icon.set_text(random.choice(pending_status))
        elif result_code == "active":
            icon.set_text(("success_icon", "\u2713"))
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            icon.set_text(("error_icon", "?"))
