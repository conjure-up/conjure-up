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

import q

class ServiceWalkthroughView(WidgetWrap):
    def __init__(self, app, deploy_controller,
                 placement_controller):
        self.app = app
        self.deploy_controller = deploy_controller
        self.placement_controller = placement_controller
        self.walkthrough_widgets = []
        self.current_widget_idx = 0
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):
        self.continue_button = PlainButton("Accept defaults and continue",
                                           self.handle_done)
        self.walkthrough_widgets = [ServiceWalkthroughWidget(
            s, self.app.metadata_controller, self.deploy_controller)
                                for s in self.placement_controller.services()]
        pile_ws = [
            Padding.center_90(
                Instruction(
                    "Services Walkthrough")),
            Padding.center_90(HR()),
            Padding.center_50(self.continue_button)] + \
            [Padding.center_70(w) for w in
             self.walkthrough_widgets]
        self.pile = Pile(pile_ws)
        self.select_widget_at(self.current_widget_idx)
        return Filler(self.pile, valign="top")

    def update(self, *args, **kwargs):
        for w in self.walkthrough_widgets:
            w.update()
        EventLoop.set_alarm_in(1, self.update)

    def select_widget_at(self, idx, prev_idx=None):
        if idx >= len(self.walkthrough_widgets):
            return False
        q.q(idx, prev_idx)
        self.pile.selected_index = self.current_widget_idx
        cw = self.walkthrough_widgets[self.current_widget_idx]
        cw.set_selected(True)
        cw.update()
        
        if prev_idx:
            pw = self.walkthrough_widgets[prev_idx]
            pw.set_selected(False)
            pw.update()
        return True
        
    def handle_done(self, button):
        self.deploy_controller.finish()

    def handle_service_scale_change(self, service, value):
        pass

    def handle_service_ctype_change(self, service, value):
        pass

    def handle_service_deploy(self, service):
        self.current_widget_idx += 1
        if not self.select_widget_at(self.current_widget_idx,
                                     self.current_widget_idx - 1):
            self.pile.selected_index = 2

