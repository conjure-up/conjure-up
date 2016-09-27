# Copyright 2016 Canonical, Ltd.
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

import json
import logging
import os

from bundleplacer.maas import MaasMachine

log = logging.getLogger('bundleplacer')


class FakeMaasState:
    """ A fake MAAS fixture for quickly testing bundle placement
    against a set of machines
    """

    server_hostname = "fake.maas"

    def machines(self, state=None, constraints=None):
        fakepath = '/usr/share/bundle-placer/share'
        fn = os.path.join(fakepath, "maas-machines.json")
        if not os.path.exists(fn):
            fn = os.path.join("share", "maas-machines.json")
        with open(fn) as f:
            try:
                nodes = json.load(f)
            except:
                log.exception("Error loading JSON")
                return []
        return [MaasMachine(-1, m) for m in nodes
                if m['hostname'] != 'juju-bootstrap.maas']

    def invalidate_nodes_cache(self):
        "no op"

    def machines_summary(self):
        return "no summary for fake state"

    def get_server_config(self, param):
        return dict(maas_name='fake maas')
