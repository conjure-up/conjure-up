from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import done_btn
from urwid import (WidgetWrap,  Filler, Pile)
from conjure.ui.widgets.step import StepWidget
from conjure.ui.widgets.stepmodel import StepModelWidget


class StepsView(WidgetWrap):

    def __init__(self, app, steps, cb=None):
        """ init

        Arguments:
        cb: process step callback
        """
        self.app = app
        self.cb = cb
        self.steps = steps
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
        widgets = []
        for idx, step in enumerate(self.steps):
            self.app.log.debug("Step widget processing: {}".format(step))
            if not step.viewable:
                self.app.log.debug("{} is not viewable, skipping".format(
                    step))
                continue
            step.widget = StepModelWidget(step)
            w = StepWidget(self.app,
                           idx,
                           step,
                           self.cb)
            self.app.log.debug("Widgeting Step: {}".format(w))
            widgets.append(w)
        return Pile(widgets)

    def done(self, *args):
        self.cb({}, done=True)
