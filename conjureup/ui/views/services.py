import random
from urwid import (Text, WidgetWrap)
from ubuntui.widgets.juju.service import ServiceWidget
from ubuntui.widgets.table import Table
from ubuntui.utils import Color
from conjureup.api.models import model_status


class ServicesView(WidgetWrap):

    view_columns = [
        ('Icon', "", 2),
        ('Name', "Service", 0),
        ('AgentStatus', "Status", 20),
        ('PublicAddress', "IP", 20),
        ('Machine', "Machine", 20),
    ]

    def __init__(self, app):
        self.app = app
        self.deployed = {}
        self.unit_w = None
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

        self.refresh_nodes()

    def refresh_nodes(self):
        """ Adds services to the view if they don't already exist
        """
        status = model_status()
        for name, service in sorted(status['applications'].items()):
            service_w = ServiceWidget(name, service)
            for unit in service_w.Units:
                services_list = []
                try:
                    unit_w = self.deployed[unit._name]
                except:
                    self.deployed[unit._name] = unit
                    unit_w = self.deployed[unit._name]
                    for k, label, width in self.view_columns:
                        if width == 0:
                            services_list.append(getattr(unit_w, k))
                        else:
                            if not hasattr(unit_w, k):
                                continue
                            services_list.append(('fixed', width,
                                                  getattr(unit_w, k)))

                    self.table.addColumns(unit._name, services_list)
                    if not hasattr(unit_w, 'WorkloadInfo'):
                        continue
                    self.table.addColumns(
                        unit._name,
                        [
                            ('fixed', 5, Text("")),
                            Color.info_context(
                                unit_w.WorkloadInfo)
                        ],
                        force=True)
                self.update_ui_state(unit_w, unit._unit)

    def status_icon_state(self, agent_state):
        if agent_state == "maintenance" \
           or agent_state == "allocating" \
           or agent_state == "executing":
            pending_status = [("pending_icon", "\N{CIRCLED BULLET}"),
                              ("pending_icon", "\N{CIRCLED WHITE BULLET}"),
                              ("pending_icon", "\N{FISHEYE}")]
            status = random.choice(pending_status)
        elif agent_state == "waiting":
            status = ("pending_icon", "\N{HOURGLASS}")
        elif agent_state == "idle" \
                or agent_state == "active":
            status = ("success_icon", "\u2713")
        elif agent_state == "blocked":
            status = ("error_icon", "\N{BLACK FLAG}")
        elif agent_state == "unknown":
            status = ("error_icon", "\N{DOWNWARDS BLACK ARROW}")
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            status = ("error_icon", "?")
        return status

    def update_ui_state(self, unit_w, unit):
        """ Updates individual machine information

        Arguments:
        service: current service
        unit_w: UnitInfo widget
        unit: current unit for service
        """
        try:
            unit_w.Machine.set_text(unit.get('machine', '-'))
            unit_w.PublicAddress.set_text(unit['public-address'])
            unit_w.WorkloadInfo.set_text(unit['workload-status']['info'])
            if unit['workload-status']['status'] != 'unknown':
                unit_w.AgentStatus.set_text(unit['workload-status']['status'])
                unit_w.Icon.set_text(
                    self.status_icon_state(unit['workload-status']['status']))
            else:
                unit_w.AgentStatus.set_text(unit['agent-status']['status'])
                unit_w.Icon.set_text(
                    self.status_icon_state(unit['agent-status']['status']))
        except Exception as e:
            self.app.log.exception(e)
            self.app.ui.show_exception_message(e)
