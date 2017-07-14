from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import done_btn
from ubuntui.widgets.hr import HR
from urwid import Pile

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.step import StepResult


class ShowStepsView(BaseView):
    title = "Additional Application Configuration"
    excerpt = ("Please provide the information below, which will "
               "be used for the post-deploy configuration.")

    def build_widget(self):
        self.step_pile = Pile([
            HR(),
            Padding.line_break(''),
        ])
        return self.step_pile

    def add_step(self, step_widget):
        self.step_pile.contents.append((step_widget, self.step_pile.options()))
        self.step_pile.focus_position = len(self.step_pile.contents) - 1


class RunStepsView(BaseView):
    title = "Running Post-Deploy Steps"
    excerpt = "Please wait while the post-deploy steps are run."

    def build_widget(self):
        self.widgets = {}
        widgets = [
            HR(),
            Padding.line_break(''),
        ]
        for step in app.steps:
            widget = StepResult(step)
            self.widgets[step.name] = widget
            widgets.append(widget)
        self.pile = Pile(widgets)
        return self.pile

    def mark_running(self, step):
        self.widgets[step.name].mark_running()

    def mark_complete(self, step):
        self.widgets[step.name].mark_complete(step.result)

    def show_summary_button(self, callback):
        self.pile.contents.append(
            (Padding.center_20(Color.button_primary(
                done_btn(on_press=lambda *a, **kw: callback(),
                         label="View Summary"),
                focus_map='button_primary focus')),
             self.pile.options()))
        self.pile.focus_position = len(self.widgets) + 2
