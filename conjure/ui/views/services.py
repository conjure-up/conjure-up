import logging
import random
from urwid import (Text, WidgetWrap)
from conjure.ui.widgets.service import ServiceInfoWidget
from ubuntui.widgets.table import Table
from ubuntui.utils import Color
from conjure.api.models import model_status


log = logging.getLogger('services_status')


class ServicesView(WidgetWrap):

    view_columns = [
        ('icon', "", 2),
        ('display_name', "Service", 0),
        ('agent_state', "Status", 12),
        ('public_address', "IP", 12),
        ('machine', "Machine", 12),
    ]

    def __init__(self, common):
        self.common = common
        self.deployed = {}
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

        self.refresh_nodes()

    def refresh_nodes(self):
        """ Adds services to the view if they don't already exist
        """
        status = model_status()
        for service, info in status['services'].items():
            services_list = []
            try:
                unit_w = self.deployed[service]
            except:
                self.deployed[service] = ServiceInfoWidget(service,
                                                           info)
                unit_w = self.deployed[service]
                for k, label, width in self.view_columns:
                    if width == 0:
                        services_list.append(getattr(unit_w, k))
                    else:
                        services_list.append(('fixed', width,
                                              getattr(unit_w, k)))

                    self.table.addColumns(service, services_list)
                    self.table.addColumns(
                            service,
                            [
                                ('fixed', 5, Text("")),
                                Color.frame_subheader(unit_w.workload_info)
                            ],
                            force=True)
                    self.deployed[service].update()

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
