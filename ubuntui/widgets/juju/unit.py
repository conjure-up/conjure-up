""" Represents a Single Juju unit UI widget
"""

from urwid import WidgetWrap, Text


class UnitWidget(WidgetWrap):
    def __init__(self, unit):
        """ Init

        Params:
        machine: Juju Unit Class
        """
        self.unit = unit
        _attrs = ['unit_name',
                  'workload_state',
                  'extended_agent_state',
                  'workload_info',
                  'machine_id',
                  'public_address',
                  'agent_state_info']
        for m in _attrs:
            setattr(self, m, Text(getattr(self.unit, m)))
