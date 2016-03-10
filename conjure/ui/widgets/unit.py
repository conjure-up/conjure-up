""" Unit info widget, attaches properties from unit/charm class to
urwid Text widgets
"""
import logging
from urwid import WidgetWrap, Text

log = logging.getLogger('unitinfo_w')


class UnitInfoWidget(WidgetWrap):
    def __init__(self, unit, charm_class, hwinfo):
        self.unit = unit
        self.charm_class = charm_class
        self.hwinfo = hwinfo
        self.container = Text(self.hwinfo['container'])
        self.machine = Text(self.hwinfo['machine'])
        self.arch = Text(self.hwinfo['arch'])
        self.cpu_cores = Text(self.hwinfo['cpu_cores'])
        self.mem = Text(self.hwinfo['mem'])
        self.storage = Text(self.hwinfo['storage'])
        self.display_name = Text(self.charm_class.display_name)
        self.agent_state = Text(self.unit.agent_state)
        self.public_address = Text(self.unit.public_address)
        self.extended_agent_state = Text(self.unit.extended_agent_state)
        self.workload_info = Text(self.unit.workload_info)
        self.icon = Text("")
