# Copyright 2015-2016 Canonical, Ltd.
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


log = logging.getLogger('bundleplacer')


class Service:
    def __init__(self, service_name, charm_source, summary_future,
                 constraints, depends, conflicts,
                 allowed_assignment_types, num_units, options,
                 allow_multi_units, subordinate, required, relations):
        self.service_name = service_name
        self.charm_name = '-'.join(charm_source.split('/')[-1].split('-')[:-1])
        self.charm_source = charm_source
        self.summary_future = summary_future
        self._summary = "Loading summary…"
        self.constraints = constraints
        self.depends = depends
        self.conflicts = conflicts
        self.allowed_assignment_types = allowed_assignment_types
        self.num_units = num_units
        self.options = options
        self.allow_multi_units = allow_multi_units
        self.subordinate = subordinate
        self.is_core = required
        self.isolate = True if not subordinate else False
        self.relations = relations

    @property
    def summary(self):
        if self.summary_future and self.summary_future.done():
            self._summary = self.summary_future.result()
        return self._summary

    @property
    def display_name(self):
        return "{} ({})".format(self.service_name,
                                self.charm_source)

    def required_num_units(self):
        return self.num_units

    def __repr__(self):
        return "<Service {}>".format(self.service_name)

    def __eq__(self, other):
        me = self.charm_source + self.service_name
        them = other.charm_source + other.service_name
        return me == them

    def __hash__(self):
        """We assume that we won't instantiate multiple Charm objects for the
        same class that have different properties.
        """
        return hash(self.charm_source + self.service_name)
