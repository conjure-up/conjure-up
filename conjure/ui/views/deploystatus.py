import random
from urwid import (Text, WidgetWrap)
from ubuntui.widgets.juju.service import ServiceWidget
from ubuntui.widgets.table import Table
from ubuntui.utils import Color, Padding
from conjure.api.models import model_status


class DeployStatusView(WidgetWrap):

    def __init__(self, app):
        self.app = app
        self.deployed = {}
        self.unit_w = None
        self.table = Table()
        super().__init__(Padding.center_80(self.table.render()))
        self.refresh_nodes()

    def refresh_nodes(self):
        """ Adds services to the view if they don't already exist
        """
        status = model_status()
        for name, service in sorted(status['Services'].items()):
            service_w = ServiceWidget(name, service)
            for unit in service_w.Units:
                try:
                    unit_w = self.deployed[unit._name]
                except:
                    self.deployed[unit._name] = unit
                    unit_w = self.deployed[unit._name]
                    self.table.addColumns(
                        unit._name,
                        [
                            ('fixed', 3, getattr(unit_w, 'Icon')),
                            ('fixed', 50, getattr(unit_w, 'Name')),
                            ('fixed', 20, getattr(unit_w, 'AgentStatus'))
                        ]
                    )

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
            unit_w.Machine.set_text(unit.get('Machine', '-'))
            unit_w.PublicAddress.set_text(unit['PublicAddress'])
            unit_w.WorkloadInfo.set_text(unit['WorkloadStatus']['Info'])
            if unit['WorkloadStatus']['Status'] != 'unknown':
                unit_w.AgentStatus.set_text(unit['WorkloadStatus']['Status'])
                unit_w.Icon.set_text(
                    self.status_icon_state(unit['WorkloadStatus']['Status']))
            else:
                unit_w.AgentStatus.set_text(unit['AgentStatus']['Status'])
                unit_w.Icon.set_text(
                    self.status_icon_state(unit['AgentStatus']['Status']))
        except Exception as e:
            self.app.log.exception(e)
            self.app.ui.show_exception_message(e)
