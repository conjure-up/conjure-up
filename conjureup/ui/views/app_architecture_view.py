""" Application Architecture / Machine Placement View

"""
import logging

import q
from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.ui.widgets.machines_list import MachinesList

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR

log = logging.getLogger('conjure')


class AppArchitectureView(WidgetWrap):

    def __init__(self, application, controller):
        self.controller = controller
        self.application = application
        self._assignments = []

        self.alarm = None
        self.widgets = self.build_widgets()
        self.description_w = Text("")
        self.buttons_selected = False
        self.frame = Frame(body=self.build_widgets(),
                           footer=self.build_footer())
        super().__init__(self.frame)
        self.update()

    def selectable(self):
        return True

    def keypress(self, size, key):
        # handle keypress first, then get new focus widget
        rv = super().keypress(size, key)
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return rv

    def _swap_focus(self):
        if not self.buttons_selected:
            self.buttons_selected = True
            self.frame.focus_position = 'footer'
            self.buttons.focus_position = 3
        else:
            self.buttons_selected = False
            self.frame.focus_position = 'body'

    def build_widgets(self):
        ws = [Text("Choose where to place {} unit{} of {}".format(
            self.application.num_units,
            "" if self.application.num_units == 1 else "s",
            self.application.service_name))]

        self.machines_list = MachinesList(self.application,
                                          self.do_select,
                                          self.do_unselect,
                                          self.controller,
                                          show_only_ready=True,
                                          show_filter_box=True)
        ws.append(self.machines_list)

        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def build_footer(self):
        cancel = menu_btn(on_press=self.do_cancel,
                          label="\n  BACK\n")
        self.apply_button = menu_btn(on_press=self.do_commit,
                                     label="\n APPLY\n")
        self.buttons = Columns([
            ('fixed', 2, Text("")),
            ('fixed', 13, Color.menu_button(
                cancel,
                focus_map='button_primary focus')),
            Text(""),
            ('fixed', 20, Color.menu_button(
                self.apply_button,
                focus_map='button_primary focus')),
            ('fixed', 2, Text(""))
        ])

        footer = Pile([
            HR(top=0),
            Padding.center_90(self.description_w),
            Padding.line_break(""),
            Color.frame_footer(Pile([
                Padding.line_break(""),
                self.buttons]))
        ])

        return footer

    def update_now(self, *args):
        if len(self._assignments) == self.application.num_units:
            self.machines_list.all_assigned = True
        else:
            self.machines_list.all_assigned = False
        self.machines_list.update()

    def update(self, *args):
        self.update_now()
        self.alarm = EventLoop.set_alarm_in(1, self.update)

    def do_select(self, machine, assignment_type):
        self._assignments.append((machine,
                                  assignment_type))
        self.update_now()

    def do_unselect(self, machine):
        self._assignments = [(m, a) for (m, a) in self._assignments
                             if m != machine]
        self.update_now()

    def do_cancel(self, sender):
        self.controller.handle_sub_view_done()
        if self.alarm:
            EventLoop.remove_alarm(self.alarm)

    def do_commit(self, sender):
        self.controller.clear_placements(self.application)
        for machine, atype in self._assignments:
            self.controller.add_placement(self.application, machine, atype)

        self.controller.handle_sub_view_done()
        if self.alarm:
            EventLoop.remove_alarm(self.alarm)
