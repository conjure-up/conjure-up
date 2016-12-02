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

from enum import Enum


def label_to_atype(labels):
    """ Maps labels in metadata to assignment types

    Arguments:
    labels: List of assignment types ['LXC', 'KVM', 'BareMetal']

    Returns:
    List of mapped enumerated assignment types
    """
    atypes = []
    for label in labels:
        if isinstance(label, AssignmentType):
            atypes.append(label)
        if label.lower() == "lxc":
            atypes.append(AssignmentType.LXC)
        elif label.lower() == "baremetal":
            atypes.append(AssignmentType.BareMetal)
        elif label.lower() == "kvm":
            atypes.append(AssignmentType.KVM)
        elif label.lower() == "lxd":
            atypes.append(AssignmentType.LXD)
        else:
            return [AssignmentType.DEFAULT]
    return atypes


def atype_to_label(atypes):
    """ Maps assignmenttypes to api labels"""
    pd = {AssignmentType.DEFAULT: "",
          AssignmentType.BareMetal: "",
          AssignmentType.KVM: "kvm:",
          AssignmentType.LXD: "lxd:",
          AssignmentType.LXC: "lxc:"}
    return [pd[atype] for atype in atypes]


class OrderedEnum(Enum):

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class AssignmentType(OrderedEnum):
    # both are equivalent to not specifying a type to juju:
    DEFAULT = 1
    BareMetal = 1
    KVM = 2
    LXC = 3
    LXD = 4
