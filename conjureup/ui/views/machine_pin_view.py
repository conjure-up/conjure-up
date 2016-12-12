""" Application Architecture / Machine Placement View

"""
import logging

from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.ui.widgets.machines_list import MachinesList
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR

log = logging.getLogger('conjure')


class MachinePinView(WidgetWrap):

    def __init__(self, juju_machine_id, application, controller):
        """
        juju_machine_id: a numeric machine id for a juju machine

        application: an application currently being configured

        controller: an object that provides get_pin, set_pin,
        unset_pin and commit_machine_pin()
        """
        self.juju_machine_id = juju_machine_id
        self.application = application
        self.controller = controller

        self.buttons_selected = False

        self.frame = Frame(body=self.build_widgets(),
                           footer=self.build_footer())
        super().__init__(self.frame)
        self.update()

    def selectable(self):
        return True

    def keypress(self, size, key):
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

    def __repr__(self):
        return "MachinePinView"

    def build_widgets(self):
        self.machines_list = MachinesList(
            select_cb=self.select_machine,
            unselect_cb=self.unselect_machine,
            target_info=str(self.juju_machine_id),
            current_pin_cb=self.controller.get_pin_for_maas_machine,
            show_hardware=True,
            show_only_ready=True,
            show_filter_box=True
        )
        header = Text("Choose a MAAS machine to pin to Juju Machine {}".format(
            self.juju_machine_id))
        self.pile = Pile([header,
                          self.machines_list])
        return Padding.center_90(Filler(self.pile,
                                        valign="top"))

    def build_footer(self):
        cancel = menu_btn(on_press=self.do_cancel,
                          label="\n  BACK\n")
        self.apply_button = menu_btn(on_press=self.do_done,
                                     label="\n DONE\n")
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
            Padding.line_break(""),
            Color.frame_footer(Pile([
                Padding.line_break(""),
                self.buttons]))
        ])

        return footer

    def update(self):
        self.machines_list.update()

    def select_machine(self, maas_machine):
        self.controller.set_pin(self.juju_machine_id, maas_machine)

    def unselect_machine(self, maas_machine):
        self.controller.unset_pin(maas_machine)

    def do_cancel(self, sender):
        self.controller.handle_sub_view_done()

    def do_done(self, sender):
        self.controller.handle_sub_view_done()
