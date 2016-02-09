# Copyright 2014-2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Unit info widget
"""

from urwid import WidgetWrap, Text


class UnitInfoWidget(WidgetWrap):
    def __init__(self, unit):
        self.agent_name = Text(self.unit.unit_name)
        self.agent_state = Text(self.unit.agent_state)
        self.public_address = Text(self.unit.public_address)
        self.icon = Text("")
