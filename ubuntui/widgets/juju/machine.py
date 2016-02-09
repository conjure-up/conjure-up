""" Represents a Single Juju machine UI widget
"""

from urwid import WidgetWrap, Text


class MachineWidget(WidgetWrap):
    def __init__(self, machine):
        """ Init

        Params:
        machine: Juju Machine Class (see https://git.io/vg0Xe)
        """
        self.machine = machine
        _attrs = ['machine_id',
                  'cpu_cores',
                  'storage',
                  'mem',
                  'agent',
                  'agent_state',
                  'agent_state_info',
                  'agent_version',
                  'dns_name',
                  'err',
                  'has_vote',
                  'wants_vote']
        for m in _attrs:
            setattr(self, m, Text(getattr(self.machine, m)))
