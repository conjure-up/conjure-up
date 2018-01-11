""" Application Architecture / Machine Placement View

"""
from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.machines_list import MachinesList


class MachinePinView(BaseView):
    title = "Pin Machine"

    def __init__(self, juju_machine_id, application, controller, close_cb):
        """
        juju_machine_id: a numeric machine id for a juju machine

        application: an application currently being configured

        controller: an object that provides get_pin, set_pin,
        unset_pin and commit_machine_pin()
        """
        self.subtitle = ("Choose a MAAS machine to pin "
                         "Juju Machine {} to".format(juju_machine_id))
        self.prev_screen = close_cb
        self.submit = close_cb
        self.juju_machine_id = juju_machine_id
        self.application = application
        self.controller = controller
        super().__init__()
        self.update()

    def build_widget(self):
        self.machines_list = MachinesList(
            select_cb=self.select_machine,
            unselect_cb=self.unselect_machine,
            target_info=str(self.juju_machine_id),
            current_pin_cb=self.controller.get_pin_for_maas_machine,
            constraints=self.controller.get_constraints(
                self.juju_machine_id),
            show_hardware=True,
            show_only_ready=True,
            show_filter_box=True
        )
        return self.machines_list

    def build_buttons(self):
        return [self.button('DONE', self.submit)]

    def update(self):
        self.machines_list.update()

    def select_machine(self, maas_machine):
        self.controller.set_pin(self.juju_machine_id, maas_machine)

    def unselect_machine(self, maas_machine):
        self.controller.unset_pin(maas_machine)
