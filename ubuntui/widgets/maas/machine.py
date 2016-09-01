""" Represents a Single MAAS node UI widget
"""

from urwid import WidgetWrap, Text


class MachineWidget(WidgetWrap):

    def __init__(self, machine):
        """ Init

        Params:
        machine: Maas Machine class
        """
        self.machine = machine
        _attrs = ['hostname',
                  'status',
                  'zone',
                  'cpu_count',
                  'storage',
                  'architecture',
                  'memory',
                  'power_type',
                  'power_state',
                  'system_id',
                  'ip_addresses',
                  'macaddress_set',
                  'tag_names',
                  'owner']
        for m in _attrs:
            if isinstance(m, list):
                continue
            setattr(self, m, Text(str(self.machine.get(m))))
