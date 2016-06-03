from conjure.ui.widgets.step import StepWidget
from ubuntui.utils import Padding
from ubuntui.widgets.table import Table
from urwid import WidgetWrap
import random


class StepsView(WidgetWrap):

    def __init__(self, app, steps):
        self.app = app
        self.table = Table()

        self.steps_queue = steps
        for k, v in self.steps_queue.items():
            self.steps_queue[k] = StepWidget(v)
            self.table.addColumns(
                k,
                [
                    ('fixed', 3, self.steps_queue[k].icon),
                    self.steps_queue[k].title,
                ]
            )
            self.table.addColumns(
                k,
                [
                    ('weight', 1, Padding.left(self.steps_queue[k].result,
                                               left=4))

                ], force=True
            )

        super().__init__(Padding.center_80(self.table.render()))

    def update_step_message(self, key, msg):
        """ Updates the return results from a step
        """
        self.steps_queue[key].result.set_text(('info_context', msg))

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
