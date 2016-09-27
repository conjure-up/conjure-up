#
# Copyright 2014 Canonical, Ltd.
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

import logging
from enum import Enum, IntEnum, unique

log = logging.getLogger('bundleplacer')


class InstallState(IntEnum):
    RUNNING = 0
    NODE_WAIT = 1


@unique
class ControllerState(IntEnum):

    """Names for current screen state"""
    INSTALL_WAIT = 0
    PLACEMENT = 1
    SERVICES = 2
    ADD_SERVICES = 3


class ServiceState(Enum):

    """ Service interaction states """
    REQUIRED = 0
    OPTIONAL = 1
    CONFLICTED = 2
