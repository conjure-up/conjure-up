from conjure.ui.widgets.step import StepWidget
from ubuntui.utils import Padding, Color
from ubuntui.widgets.table import Table
from ubuntui.widgets.buttons import submit_btn, done_btn
from urwid import WidgetWrap
import random


class StepsView(WidgetWrap):

    def __init__(self, app, steps, cb=None):
        """ init

        Arguments:
        cb: process step callback
        """
        self.app = app
        self.table = Table()
        self.cb = cb

        self.steps_queue = steps
        for k, v in self.steps_queue.items():
            step_metadata = StepWidget(v['step_metadata'])
            if not step_metadata.viewable:
                continue
            self.table.addColumns(
                k,
                [
                    ('fixed', 3, step_metadata.icon),
                    step_metadata.description,
                ]
            )
            # Need to still prompt for the user to submit
            # even though no questions are asked
            if len(step_metadata.additional_input) == 0:
                self.table.addRow(
                    Padding.right_20(
                        Color.button_primary(
                            submit_btn(on_press=self.submit,
                                       user_data=step_metadata),
                            focus_map='button_primary focus')), False)
            for i in step_metadata.additional_input:
                self.table.addRow(Padding.line_break(""), False)
                self.table.addColumns(
                    k,
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
                            submit_btn(on_press=self.submit,
                                       user_data=step_metadata),
                            focus_map='button_primary focus')), False)
                self.table.addRow(Padding.line_break(""), False)

        self.table.addRow(Padding.center_20(
                        Color.button_primary(
                            done_btn(on_press=self.done, label="View Summary"),
                            focus_map='button_primary focus')))
        super().__init__(Padding.center_80(self.table.render()))

    def done(self, *args):
        self.cb({}, done=True)

    def submit(self, btn, stepwidget_metadata):
        self.cb(stepwidget_metadata)

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
