from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import done_btn
from urwid import (WidgetWrap,  Filler, Pile)


class StepsView(WidgetWrap):

    def __init__(self, app, steps, cb=None):
        """ init

        Arguments:
        cb: process step callback
        """
        self.app = app
        self.cb = cb
        self.steps = steps
        self.step_pile = Pile([
            Padding.center_90(HR()),
            Padding.line_break(""),
            Padding.center_90(Pile(self.steps)),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ])
        super().__init__(Filler(self.step_pile, valign="top"))

    @property
    def current_summary_button_index(self):
        """ Returns the pile index where the summary button is located
        """
        return self.step_pile.contents.index(
            self.step_pile.contents[len(self.step_pile.contents)-1])

    def buttons(self):
        buttons = [
            Color.button_primary(
                done_btn(on_press=self.done, label="View Summary"),
                focus_map='button_primary focus')
        ]
        return Pile(buttons)

    def done(self, *args):
        self.cb({}, done=True)
