from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)
from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import submit_btn, done_btn
from urwid import (WidgetWrap, Text, Filler, Pile, Columns)


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
        self.cb = cb
        self.steps_queue = steps
        _pile = [
            Padding.center_90(HR()),
            Padding.line_break(""),
            Padding.center_90(self.build_steps()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))

    def buttons(self):
        buttons = [
            Color.button_primary(
                done_btn(on_press=self.done, label="View Summary"),
                focus_map='button_primary focus')
        ]
        return Pile(buttons)

    def build_steps(self):
        rows = []
        for step_model in self.steps_queue:
            step_widget = self.add_step_widget(step_model)
            rows.append(
                Columns(
                    [
                        ('fixed', 3, step_widget['icon']),
                        step_widget['description'],
                    ], dividechars=1
                )
            )

            # Need to still prompt for the user to submit
            # even though no questions are asked
            if len(step_widget['additional_input']) == 0:
                rows.append(
                    Padding.right_20(
                        Color.button_primary(
                            submit_btn(on_press=self.submit,
                                       user_data=(step_model, step_widget)),
                            focus_map='button_primary focus')))
                rows.append(HR())

            for i in step_widget['additional_input']:
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
                rows.append(
                    Padding.right_20(
                        Color.button_primary(
                            submit_btn(
                                on_press=self.submit,
                                user_data=(step_model, step_widget)),
                            focus_map='button_primary focus')))
                rows.append(HR())

        return Pile(rows)

    def add_step_widget(self, step_model):
        if not step_model.viewable:
            self.app.log.debug("{} is not viewable, skipping".format(
                step_model))
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
            icon.set_text(("pending_icon", "\N{HOURGLASS}"))
        elif result_code == "active":
            icon.set_text(("success_icon", "\N{BALLOT BOX WITH CHECK}"))
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            icon.set_text(("error_icon", "?"))
