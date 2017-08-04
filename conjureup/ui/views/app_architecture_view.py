""" Application Architecture View

"""
import copy
import logging
from collections import defaultdict

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.app_config import app
from conjureup.juju import (
    constraints_from_dict,
    constraints_to_dict,
    get_cloud_types_by_name
)
from conjureup.ui.views.machine_pin_view import MachinePinView
from conjureup.ui.widgets.juju_machines_list import JujuMachinesList

log = logging.getLogger('conjure')


class AppArchitectureView(WidgetWrap):

    def __init__(self, application, controller):
        """
        application: a Service instance representing a juju application

        controller: a DeployGUIController instance
        """
        self.controller = controller
        self.application = application

        self.header = "Architecture"
        # Shadow means temporary to the view, they are committed to
        # the controller if the user chooses OK

        # {machine_id : [(app, assignmenttype) ...]
        self.shadow_assignments = defaultdict(list)
        for machine_id, al in self.controller.assignments.items():
            for (a, at) in al:
                if a == self.application:
                    self.shadow_assignments[machine_id].append((a, at))

        # {juju_machine_id : maas machine id}
        self.shadow_pins = copy.copy(controller.maas_machine_map)
        self.machine_pin_view = None

        self._machines = copy.deepcopy(app.metadata_controller.bundle.machines)

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

    def __repr__(self):
        return "App Architecture View for {}".format(
            self.application.service_name)

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
        cloud_type = get_cloud_types_by_name()[app.provider.cloud]
        controller_is_maas = cloud_type == 'maas'
        if controller_is_maas:
            extra = (" Press enter on a machine ID to pin it to "
                     "a specific MAAS node.")
        else:
            extra = ""
        ws = [Text("Choose where to place {} unit{} of {}.{}".format(
            self.application.num_units,
            "" if self.application.num_units == 1 else "s",
            self.application.service_name,
            extra))]

        self.juju_machines_list = JujuMachinesList(
            self.application,
            self._machines,
            self.do_assign,
            self.do_unassign,
            self.add_machine,
            self.remove_machine,
            self,
            show_filter_box=True,
            show_pins=controller_is_maas)
        ws.append(self.juju_machines_list)

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
        if self.machine_pin_view:
            self.machine_pin_view.update()
            return

        n_assigned = len(self.get_all_shadow_assignments(self.application))
        if n_assigned == self.application.num_units:
            self.juju_machines_list.all_assigned = True
        else:
            self.juju_machines_list.all_assigned = False
        self.juju_machines_list.update()

    def update(self, *args):
        self.update_now()
        self.alarm = EventLoop.set_alarm_in(1, self.update)

    def do_assign(self, juju_machine_id, assignment_type):
        self.shadow_assignments[juju_machine_id].append((self.application,
                                                         assignment_type))
        self.update_now()

    def do_unassign(self, juju_machine_id):
        self.shadow_assignments[juju_machine_id] = [
            (a, at) for (a, at)
            in self.shadow_assignments[juju_machine_id]
            if a != self.application]
        self.update_now()

    def get_all_assignments(self, juju_machine_id):
        """merge committed assignments of other apps with shadow assignments
        of this app
        return list of tuples [(application, assignmenttype)]
        """
        all_assignments = [(a, at) for (a, at)
                           in self.controller.assignments[juju_machine_id]
                           if a != self.application]
        return all_assignments + self.shadow_assignments[juju_machine_id]

    def get_shadow_assignments(self, application, juju_machine_id):
        return self.shadow_assignments[juju_machine_id]

    def get_all_shadow_assignments(self, application):
        all_assignments = []
        for j_m_id, al in self.shadow_assignments.items():
            all_assignments += al
        return [(a, at) for (a, at)
                in all_assignments if a == application]

    def add_machine(self):
        md = dict(series=app.metadata_controller.bundle.series)
        self._machines[str(len(self._machines))] = md

    def remove_machine(self):
        raise Exception("TODO")

    def get_shadow_pin(self, juju_machine_id):
        return self.shadow_pins.get(juju_machine_id, None)

    get_pin = get_shadow_pin

    def get_pin_for_maas_machine(self, maas_machine):
        for j_id, m in self.shadow_pins.items():
            if m == maas_machine:
                return j_id
        return None

    def show_pin_chooser(self, juju_machine_id):
        app.ui.set_header("Pin Machine {}".format(juju_machine_id))
        self.machine_pin_view = MachinePinView(
            juju_machine_id, self.application, self)
        self.update_now()
        app.ui.set_body(self.machine_pin_view)

    def handle_sub_view_done(self):
        app.ui.set_header(self.header)
        self.machine_pin_view = None
        self.update_now()
        app.ui.set_body(self)

    def set_pin(self, juju_machine_id, maas_machine):
        self.shadow_pins[juju_machine_id] = maas_machine

    def unset_pin(self, maas_machine):
        self.shadow_pins = {j_m_id: m for j_m_id, m in
                            self.shadow_pins.items()
                            if m != maas_machine}

    def get_constraints(self, juju_machine_id):
        cstr = self._machines[juju_machine_id].get(
            'constraints', {})
        return constraints_to_dict(cstr)

    def set_constraint(self, juju_machine_id, key, value):
        md = self._machines[juju_machine_id]
        cd = constraints_to_dict(md.get('constraints', ""))
        cd[key] = value
        md['constraints'] = constraints_from_dict(cd)
        return md

    def clear_constraint(self, juju_machine_id, key):
        md = self._machines[juju_machine_id]
        cd = constraints_to_dict(md.get('constraints', ""))
        if key in cd:
            del cd[key]
        md['constraints'] = constraints_from_dict(cd)
        return md

    def do_cancel(self, sender):
        self.controller.handle_sub_view_done()
        if self.alarm:
            EventLoop.remove_alarm(self.alarm)

    def do_commit(self, sender):
        """Commit changes to shadow assignments, constraints, and pins"""
        app.metadata_controller.bundle.machines = self._machines

        self.controller.clear_assignments(self.application)
        for juju_machine_id, al in self.shadow_assignments.items():
            for application, atype in al:
                assert application == self.application
                self.controller.add_assignment(self.application,
                                               juju_machine_id, atype)

        self.controller.clear_machine_pins()
        for j_m_id, m in self.shadow_pins.items():
            self.controller.set_machine_pin(j_m_id, m)

        self.controller.handle_sub_view_done()
        if self.alarm:
            EventLoop.remove_alarm(self.alarm)
