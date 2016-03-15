""" Represents a Single Juju unit UI widget
"""

from urwid import Text


class UnitWidget:
    def __init__(self, name, unit):
        """ Init

        Params:
        machine: Juju Unit Class
        """
        self._unit = unit
        self._name = name
        self.Name = Text(self._name)
        self.AgentState = Text(unit['AgentState'])
        self.PublicAddress = Text(unit['PublicAddress'])
        self.Machine = Text(unit['Machine'])
        self.AgentStateInfo = Text(unit['AgentStateInfo'])
        self.WorkloadInfo = Text(unit['Workload']['Info'])
        self.WorkloadStatus = Text(unit['Workload']['Status'])
        self.Icon = Text("")
