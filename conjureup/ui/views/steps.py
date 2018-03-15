from ubuntui.widgets.hr import HR
from urwid import Columns, Pile, Text

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.step import StepResult


class ShowStepsView(BaseView):
    title = "Configure Spell"
    subtitle = ("Please provide the information below, which will "
                "be used for the post-deploy configuration.")

    def __init__(self, submit_cb, back_cb):
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        super().__init__()

    def build_widget(self):
        return []

    def add_step(self, step_widget):
        self.widget.contents.append((step_widget, self.widget.options()))
        self.widget.focus_position = len(self.widget.contents) - 1


class RunStepsView(BaseView):
    title = "Running Post-Deploy Steps"
    subtitle = "Please wait while the post-deploy steps are run."
    show_back_button = False

    def build_widget(self):
        self.widgets = {}
        rows = [
            Columns([
                ('fixed', 3, Text('')),
                ('weight', 0.1, Text('Application')),
                ('weight', 0.4, Text('Result'))
            ], dividechars=5),
            HR(),
        ]
        for step in app.all_steps:
            if not step.has_after_deploy:
                continue
            widget = StepResult(step)
            self.widgets[step.name] = widget
            rows.extend([
                widget,
                HR(),
            ])
        self.pile = Pile(rows)
        return self.pile

    def mark_step_running(self, step):
        self.widgets[step.name].mark_running()

    def mark_step_complete(self, step):
        self.widgets[step.name].mark_complete(step.result)

    def mark_complete(self):
        app.ui.set_header(title="Post-Deploy Steps Complete",
                          excerpt="Your deployment is now complete")
        self.set_footer("Your big software is deployed, "
                        "press the (Q) key to exit.")
        self._swap_focus()
