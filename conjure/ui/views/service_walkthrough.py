""" Service Walkthrough view

List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import WidgetWrap, Pile, Filler
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.text import Instruction
from ubuntui.widgets.hr import HR
from ubuntui.utils import Padding
from ubuntui.ev import EventLoop

from conjure.ui.widgets.service_walkthrough_widget import (
    ServiceWalkthroughWidget
)


class ServiceWalkthroughView(WidgetWrap):
    def __init__(self, app, placement_controller, done_cb):
        self.app = app
        self.placement_controller = placement_controller
        self.done_cb = done_cb
        self.walkthrough_widgets = []
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):
        self.continue_button = PlainButton("Accept defaults and continue",
                                           self.handle_done)
        self.walkthrough_widgets = self.build_walkthrough_widgets()
        _pile = [
            Padding.center_90(
                Instruction(
                    "Services")),
            Padding.center_90(HR()),
            Padding.center_90(self.continue_button),
            Padding.center_90(Pile(self.walkthrough_widgets)),
        ]
        return Filler(Pile(_pile), valign="top")

    def build_walkthrough_widgets(self):
        ws = []

        for service in self.placement_controller.services():
            ws.append(ServiceWalkthroughWidget(service,
                                               self.app.metadata_controller,
                                               self.handle_scale_change,
                                               self.handle_ctype_change))
        return ws

    def update(self, *args, **kwargs):
        for w in self.walkthrough_widgets:
            w.update()
        EventLoop.set_alarm_in(1, self.update)

    def handle_done(self, button):
        self.done_cb()

    def handle_scale_change(self, service, value):
        ""

    def handle_ctype_change(self, service, value):
        ""
