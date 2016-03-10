from operator import attrgetter
import logging
import random
from urwid import (Text, WidgetWrap)
from conjure.ui.widgets import UnitInfoWidget
from ubuntui.widgets.table import Table
from ubuntui.utils import Color


log = logging.getLogger('services_status')


class ServicesView(WidgetWrap):

    view_columns = [
        ('icon', "", 2),
        ('display_name', "Service", 0),
        ('agent_state', "Status", 12),
        ('public_address', "IP", 12),
        ('machine', "Machine", 12),
        ('container', "Container", 12),
        ('arch', "Arch ", 12),
        ('cpu_cores', "Cores", 12),
        ('mem', "Mem ", 12),
        ('storage', "Storage", 12)
    ]

    def __init__(self, nodes, juju_state, maas_state, config):
        self.deployed = {}
        self.nodes = [] if nodes is None else nodes
        self.juju_state = juju_state
        self.maas_state = maas_state
        self.unit_w = None
        self.log_cache = None
        self.table = Table()

        headings = []
        for key, label, width in self.view_columns:
            # If no width assume ('weight', 1, widget)
            if width == 0:
                headings.append(Color.column_header(Text(label)))
            else:
                headings.append(
                    ('fixed', width, Color.column_header(Text(label))))
        self.table.addHeadings(headings)
        super().__init__(self.table.render())

        self.refresh_nodes(self.nodes)

    def refresh_nodes(self, nodes):
        """ Adds services to the view if they don't already exist
        """
        for node in nodes:
            services_list = []
            charm_class, service = node
            if len(service.units) > 0:
                for u in sorted(service.units, key=attrgetter('unit_name')):
                    # Refresh any state changes
                    try:
                        unit_w = self.deployed[u.unit_name]
                    except:
                        hwinfo = self._get_hardware_info(u)
                        self.deployed[u.unit_name] = UnitInfoWidget(
                            u,
                            charm_class,
                            hwinfo)
                        unit_w = self.deployed[u.unit_name]
                        for k, label, width in self.view_columns:
                            if width == 0:
                                services_list.append(getattr(unit_w, k))
                            else:
                                services_list.append(('fixed', width,
                                                      getattr(unit_w, k)))

                        self.table.addColumns(u.unit_name, services_list)
                        self.table.addColumns(
                            u.unit_name,
                            [
                                ('fixed', 5, Text("")),
                                Color.frame_subheader(unit_w.workload_info)
                            ],
                            force=True)
                    self.update_ui_state(charm_class, u,
                                         unit_w)

    def status_icon_state(self, charm_class, unit):
        # unit.agent_state may be "pending" despite errors elsewhere,
        # so we check for error_info first.
        # if the agent_state is "error", _detect_errors returns that.
        error_info = self._detect_errors(unit, charm_class)

        if error_info:
            status = ("error_icon", "\N{TETRAGRAM FOR FAILURE}")
        elif unit.agent_state == "pending":
            pending_status = [("pending_icon", "\N{CIRCLED BULLET}"),
                              ("pending_icon", "\N{CIRCLED WHITE BULLET}"),
                              ("pending_icon", "\N{FISHEYE}")]
            status = random.choice(pending_status)
        elif unit.agent_state == "installed":
            status = ("pending_icon", "\N{HOURGLASS}")
        elif unit.agent_state == "started":
            status = ("success_icon", "\u2713")
        elif unit.agent_state == "stopped":
            status = ("error_icon", "\N{BLACK FLAG}")
        elif unit.agent_state == "down":
            status = ("error_icon", "\N{DOWNWARDS BLACK ARROW}")
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            status = ("error_icon", "?")
        return status

    def update_ui_state(self, charm_class, unit, unit_w):
        """ Updates individual machine information
        """
        unit_w.public_address.set_text(unit.public_address)
        unit_w.agent_state.set_text(unit.agent_state)
        unit_w.icon.set_text(self.status_icon_state(charm_class, unit))

    def _get_hardware_info(self, unit):
        """Get hardware info from juju or maas

        Returns list of text and formatting tuples
        """
        juju_machine = self.juju_state.machine(unit.machine_id)
        maas_machine = None
        if self.maas_state:
            maas_machine = self.maas_state.machine(juju_machine.instance_id)

        m = juju_machine
        if juju_machine.arch == "N/A":
            if maas_machine:
                m = maas_machine
            else:
                try:
                    return self._get_container_info(unit)
                except:
                    log.exception(
                        "failed to get container info for unit {}.".format(
                            unit))

        hw_info = self._hardware_info_for_machine(m)
        hw_info['machine'] = juju_machine.machine_id
        return hw_info

    def _get_container_info(self, unit):
        """Attempt to get hardware info of host machine for a unit that looks
        like a container.

        """
        base_machine = self.juju_state.base_machine(unit.machine_id)

        if base_machine.arch == "N/A" and self.maas_state is not None:
            m = self.maas_state.machine(base_machine.instance_id)
        else:
            m = base_machine

        # FIXME: Breaks single install status display
        # base_id, container_type, container_id = unit.machine_id.split('/')
        # ctypestr = dict(kvm="VM", lxc="Container")[container_type]

        # rl = ["{} {} (Machine {}".format(ctypestr, container_id,
        #                                  base_id)]
        try:
            container_id = unit.machine_id.split('/')[-1]
        except:
            log.exception("ERROR: base_machine is {} and m is {}, "
                          "and unit.machine_id is {}".format(
                              base_machine, m, unit.machine_id))
            return "?"

        base_id = base_machine.machine_id
        hw_info = self._hardware_info_for_machine(m)
        hw_info['machine'] = base_id
        hw_info['container'] = container_id
        return hw_info

    def _hardware_info_for_machine(self, m):
        return {"arch": m.arch,
                "cpu_cores": m.cpu_cores,
                "mem": m.mem,
                "storage": m.storage,
                "container": '-',
                "machine": 0}

    def _detect_errors(self, unit, charm_class):
        """Look in multiple places for an error.

        Return error info string if present,
        or None if no error is found
        """
        unit_machine = self.juju_state.machine(unit.machine_id)

        if unit.agent_state == "error":
            return unit.agent_state_info.lstrip()

        err_info = ""

        if unit.agent_state == 'pending' and \
           unit_machine.agent_state is '' and \
           unit_machine.agent_state_info is not None:

            # detect MAAS API errors, returned as 409 conflict:
            if "409" in unit_machine.agent_state_info:
                if charm_class.constraints is not None:
                    err_info = "Found no machines meeting constraints: "
                    err_info += ', '.join(["{}='{}'".format(k, v) for k, v
                                           in charm_class.constraints.items()])
                else:
                    err_info += "No machines available for unit."
            else:
                err_info += unit_machine.agent_state_info
            return err_info
        return None
