""" Service info widget, attaches properties from service to
urwid Text widgets
"""
import logging
from urwid import WidgetWrap, Text

log = logging.getLogger('serviceinfo_w')


class UnitInfoWidget(WidgetWrap):
    def __init__(self, name, unit):
        self.name = Text(name)
        self.machine = Text(unit.get('machine', ''))
        self.public_address = Text(unit.get('public-address', ''))
        self.workload_status = Text(unit.get('workload-status', ''))


class ServiceStatusWidget(WidgetWrap):
    def __init__(self, service_status):
        self.current = Text(service_status.get('current', ''))
        self.message = Text(service_status.get('message', ''))
        self.since = Text(service_status.get('since', ''))


class ServiceInfoWidget(WidgetWrap):
    def __init__(self, name, service):
        self.name = name
        for k in service.keys():
            if k == 'service-status':
                self.service_status = ServiceStatusWidget(service[k])
            elif k == 'units':
                self.units = [UnitInfoWidget(n, info) for n, info
                              in service.get('units').items()]
            else:
                setattr(self, k.replace('-', '_'), Text(service['k']))
        self.icon = Text("")
