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
        self.PublicAddress = Text(unit.get('public-address', ''))
        self.Machine = Text(unit.get('machine', ''))

        agent_status = unit.get('agent-status', {})
        if agent_status:
            self.AgentStatus = Text(agent_status.get('status', ''))
            self.AgentStatusInfo = Text(agent_status.get('info', ''))

        workload = unit.get('workload-status', {})
        if workload:
            self.WorkloadInfo = Text(workload.get('info', ''))
            self.WorkloadStatus = Text(workload.get('status', ''))
        self.Icon = Text("")
