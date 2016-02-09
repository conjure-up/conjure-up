""" Represents a Single Juju service UI widget
"""

from urwid import WidgetWrap, Text


class UnitWidget(WidgetWrap):
    def __init__(self, service):
        """ Init

        Params:
        machine: Juju Service Class
        """
        self.service = service
        _attrs = ['service_name',
                  'charm',
                  'exposed',
                  'networks',
                  'life']
        for m in _attrs:
            setattr(self, m, Text(getattr(self.service, m)))
