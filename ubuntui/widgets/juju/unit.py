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
        self.PublicAddress = Text(unit.get('PublicAddress', ''))
        self.Machine = Text(unit.get('Machine', ''))

        agent_status = unit.get('AgentStatus', {})
        if agent_status:
            self.AgentStatus = Text(agent_status.get('Status', ''))
            self.AgentStatusInfo = Text(agent_status.get('Info', ''))

        workload = unit.get('WorkloadStatus', {})
        if workload:
            self.WorkloadInfo = Text(workload.get('Info', ''))
            self.WorkloadStatus = Text(workload.get('Status', ''))
        self.Icon = Text("")
