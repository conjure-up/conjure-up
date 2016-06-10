from conjure.ui.widgets.step import StepWidget
from ubuntui.utils import Padding, Color
from ubuntui.widgets.table import Table
from ubuntui.widgets.buttons import submit_btn
from urwid import WidgetWrap
import random


class StepsView(WidgetWrap):

    def __init__(self, app, steps):
        self.app = app
        self.table = Table()

        self.steps_queue = steps
        for k, v in self.steps_queue.items():
            meta = StepWidget(v['step_metadata'])
            if not meta.viewable:
                continue
            self.table.addColumns(
                k,
                [
                    ('fixed', 3, meta.icon),
                    meta.description,
                ]
            )
            for i in meta.additional_input:
                self.table.addRow(Padding.line_break(""), False)
                self.table.addColumns(
                    k,
                    [
                        ('weight', 0.5, Padding.left(i['label'], left=5)),
                        ('weight', 1, Color.string_input(
                            i['input'],
                            focus_map='string_input focus')),
                        ('weight', 0.2,
                         Color.button_primary(
                             submit_btn(on_press=self.submit,
                                        user_data=i),
                             focus_map='button_primary focus'))
                    ], force=True
                )
                self.table.addRow(Padding.line_break(""), False)

        super().__init__(Padding.center_80(self.table.render()))

    def submit(self, result, data):
        import q
        q.q(result, data['input'].value)

    def update_icon_state(self, key, result_code):
        """ updates status icon

        Arguments:
        key: step key
        result_code: 3 types of results, error, waiting, complete
        """
        if result_code == "error":
            self.steps_queue[key].icon.set_text(
                ("error_icon", "\N{BLACK FLAG}"))
        elif result_code == "waiting":
            pending_status = [("pending_icon", "\N{CIRCLED BULLET}"),
                              ("pending_icon", "\N{CIRCLED WHITE BULLET}"),
                              ("pending_icon", "\N{FISHEYE}")]
            self.steps_queue[key].icon.set_text(random.choice(pending_status))
        elif result_code == "active":
            self.steps_queue[key].icon.set_text(("success_icon", "\u2713"))
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            self.steps_queue[key].icon.set_text(("error_icon", "?"))
