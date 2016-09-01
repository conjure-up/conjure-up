""" Represents a Single Juju machine UI widget
"""

from urwid import Text


class MachineWidget:

    def __init__(self, machine):
        """ Init

        Params:
        machine: Juju Machine Dictionary
        """
        self.machine = machine
        _attrs = ['Id',
                  'Hardware',
                  'Series',
                  'WantsVote',
                  'InstanceState',
                  'DNSName',
                  'HasVote',
                  'InstanceID']
        for m in _attrs:
            setattr(self, m, Text(str(self.machine.get(m))))
