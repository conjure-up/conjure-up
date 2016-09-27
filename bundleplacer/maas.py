#
# __init__.py - MAAS instance state
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
import time
from collections import Counter
from enum import Enum
from threading import RLock

from bundleplacer.async import submit
from bundleplacer.machine import Machine
from bundleplacer.utils import human_to_mb
from maasclient import MaasClient
from maasclient.auth import MaasAuth

log = logging.getLogger('bundleplacer')


def satisfies(machine, constraints):
    """Evaluates whether a MAAS machine's hardware matches constraints.

    If constraints is None or an empty dict, then any machine will be
    evaluated as satisfying the constraints.

    .. note::

        That if a machine has '*' as a value, that value satisfies
        any constraint.

    If successful the return will be (True, [])

    :rtype: tuple
    :returns: (bool, [list-of-failed constraint keys])

    """
    kmap = dict(mem='memory',
                arch='architecture',
                storage='storage',
                cpu_cores='cpu_count')
    kmap['root-disk'] = 'storage'

    cons_checks = []

    if constraints is None:
        return (True, [])

    for k, v in constraints.items():
        if k == 'arch':
            mval = machine.machine[kmap[k]]
            if mval != '*' and mval != v:
                cons_checks.append(k)
        else:
            mval = machine.machine[kmap[k]]

            if mval == '*':
                # '*' always satisfies.
                continue

            if not str(v).isdecimal():
                v = human_to_mb(v)

            if mval < v:
                cons_checks.append(k)

    rval = (len(cons_checks) == 0), cons_checks
    return rval


class MaasMachineStatus(Enum):
    """Symbolic names for maas API status numbers.

    -1, UNKNOWN is never returned by maas API. It's used here to
    denote a MaasMachine object that wasn't created from a Maas API
    return.
    """
    UNKNOWN = -1
    NEW = 0
    COMMISSIONING = 1
    FAILED_COMMISSIONING = 2
    MISSING = 3
    READY = 4
    RESERVED = 5
    # as of maas 1.7, state #s 6, and 9-15 are mapped
    # onto 6 by the view that services the nodes/
    # url. so we will only ever see '6' for any of
    # these, until sometime in the future.
    DEPLOYED = 6
    RETIRED = 7
    BROKEN = 8
    DEPLOYING = 9  # see DEPLOYED
    MAAS_1_7_ALLOCATED = 10  # the actual "ALLOCATED" state. see DEPLOYED
    FAILED_DEPLOYMENT = 11  # see DEPLOYED.
    RELEASING = 12
    FAILED_RELEASING = 13
    DISK_ERASING = 14
    FAILED_DISK_ERASING = 15
    ALLOCATED = 6  # for backward compatibility with internal uses

    def __str__(self):
        return self.name.lower()


class MaasMachine(Machine):
    """ Single maas machine """

    def __eq__(self, other):
        return self.hostname == other.hostname

    def __hash__(self):
        return hash(self.hostname)

    @property
    def hostname(self):
        """ Query hostname reported by MaaS

        :returns: hostname
        :rtype: str
        """
        return self.machine.get('hostname', '')

    @property
    def status(self):
        """ Status of machine state

        :returns: status enum
        :rtype: MaasMachineStatus
        """
        return MaasMachineStatus(self.machine.get('status',
                                                  MaasMachineStatus.UNKNOWN))

    @property
    def zone(self):
        """ Zone information

        :returns: zone information
        :rtype: dict
        """
        return self.machine.get('zone', {})

    @property
    def cpu_cores(self):
        """ Returns number of cpu-cores

        :returns: number of cpus
        :rtype: str
        """
        return self.machine.get('cpu_count', '0')

    @property
    def storage(self):
        """ Return storage

        :returns: storage size
        :rtype: str
        """
        try:
            _storage_in_gb = int(self.machine.get('storage')) / 1024
        except ValueError:
            return "N/A"
        return "{size:.2f}G".format(size=_storage_in_gb)

    @property
    def arch(self):
        """ Return architecture

        :returns: architecture type
        :rtype: str
        """
        return self.machine.get('architecture')

    @property
    def mem(self):
        """ Return memory

        :returns: memory size
        :rtype: str
        """
        try:
            _mem = int(self.machine.get('memory'))
        except ValueError:
            return "N/A"
        if _mem > 1024:
            _mem = _mem / 1024
            return "{size}G".format(size=str(_mem))
        else:
            return "{size}M".format(size=str(_mem))

    @property
    def power_type(self):
        """ Machine power type

        :returns: machines power type
        :rtype: str
        """
        return self.machine.get('power_type', 'None')

    @property
    def instance_id(self):
        """ Returns instance-id of a machine

        :returns: instance-id of machine
        :rtype: str
        """
        return self.machine.get('resource_uri', '')

    @property
    def system_id(self):
        """ Returns system id of a maas machine

        :returns: system id of machine
        :rtype: str
        """
        return self.machine.get('system_id', '')

    @property
    def ip_addresses(self):
        """ Ip addresses for machine

        :returns: ip addresses
        :rtype: list
        """
        return self.machine.get('ip_addresses', [])

    @property
    def macaddress_set(self):
        """ Macaddress set of maas machine

        :returns: list of dict(mac_address, resource_uri)
        :rtype: list
        """
        return self.machine.get('macaddress_set', [])

    @property
    def tag_names(self):
        """ Tag names for machine

        :returns: tags associated with machine
        :rtype: list
        """
        return self.machine.get('tag_names', [])

    @property
    def tag(self):
        """ Machine tag

        :returns: tag defined
        :rtype: str
        """
        return self.machine.get('tag', '')

    @property
    def owner(self):
        """ Machine owner

        :returns: owner
        :rtype: str
        """
        return self.machine.get('owner', 'root')

    def __repr__(self):
        return "<MaasMachine({dns_name},{state},{mem}," \
            "{storage},{cpus})>".format(dns_name=self.hostname,
                                        state=self.agent_state,
                                        mem=self.mem,
                                        storage=self.storage,
                                        cpus=self.cpu_cores)

    def __str__(self):
        return repr(self)

    def filter_label(self):
        d = dict(dns_name=self.hostname,
                 arch=self.arch,
                 tag=self.tag,
                 mem=self.mem,
                 storage=self.storage,
                 cpus=self.cpu_cores)
        return ("hostname:{dns_name} tag:{tag} mem:{mem} arch:{arch}"
                "storage:{storage} cores:{cpus}").format(**d)


class MaasState:
    """ Represents global MaaS state """

    def __init__(self, maas_client):
        self.maas_client = maas_client
        self._maas_client_nodes = []
        self._filtered_nodes = []
        self._nodes_lock = RLock()
        self._nodes_future = None
        self._start_time = 0
        self.server_hostname = maas_client.server_hostname

    def get_server_config(self, param):
        return self.maas_client.get_server_config(param)

    def nodes(self, constraints=None):
        """ Cache MAAS nodes
        """
        elapsed_time = time.time() - self._start_time
        if elapsed_time <= 20:
            return self._filtered_nodes

        def _do_update():
            nodes = self.maas_client.nodes
            self.invalidate_nodes_cache()
            return nodes

        if self._nodes_future:
            if self._nodes_future.done():
                with self._nodes_lock:
                    self._maas_client_nodes = self._nodes_future.result()
                self._nodes_future = None
        else:
            self._nodes_future = submit(_do_update, lambda _: None)

        if constraints:
            self._filtered_nodes = self._filter_nodes(self._maas_client_nodes,
                                                      constraints)
        else:
            self._filtered_nodes = self._maas_client_nodes

        self._start_time = time.time()
        return self._filtered_nodes

    def nodes_uncached(self, constraints=None):
        if constraints:
            return self._filter_nodes(self.maas_client.nodes)
        else:
            return self.maas_client.nodes

    def _filter_nodes(self, nodes, constraints):
        assert constraints is not None

        cd = dict(x.split('=') for x in constraints.split(' '))
        arch = cd.get('arch', None)
        tagstr = cd.get('tags', None)
        satisfying_nodes = []
        for n in self._maas_client_nodes:
            if arch:
                n_arch = n['architecture'].split('/')[0]
                if n_arch != arch:
                    continue
            if tagstr:
                c_tags = set(cd['tags'].split(','))
                n_tags = set(n['tag_names'])
                if not c_tags.issubset(n_tags):
                    continue
            satisfying_nodes.append(n)

        return satisfying_nodes

    def invalidate_nodes_cache(self):
        """Force reload on next access"""
        self._start_time = 0

    def machine(self, instance_id):
        """ Return single machine state

        :param str instance_id: machine instance_id
        :returns: machine
        :rtype: bundleplacer.maas.MaasMachine
        """
        for m in self.machines():
            if m.instance_id == instance_id:
                return m
        return None

    def machines(self, state=None, constraints=None):
        """Maas Machines

        :param state

        :param str constraints: a juju style constraints string that
        we parse for arch and tags

        :returns: machines known to Maas, except for juju bootstrap
            machine, matching state type, or all if state=None

        :rtype: list of MaasMachine

        """
        nodes = [n for n in self.nodes(constraints)
                 if n['hostname'] != 'juju-bootstrap.maas']
        all_machines = [MaasMachine(-1, m) for m in nodes]
        if state:
            return [m for m in all_machines if m.status == state]
        else:
            return all_machines

    def machines_summary(self):
        """ Returns summary of known machines and their states.
        """
        log.debug("in summary, self.nodes is {}".format(self.nodes()))
        return Counter([MaasMachineStatus(m['status'])
                        for m in self.nodes()])


def connect_to_maas(creds=None):
    if creds:
        api_host = creds['api_host']
        api_url = 'http://{}/MAAS/api/1.0'.format(api_host)
        api_key = creds['api_key']
        auth = MaasAuth(api_url=api_url,
                        api_key=api_key)
    else:
        auth = MaasAuth()
        auth.get_api_key('root')
    maas = MaasClient(auth)
    maas_state = MaasState(maas)
    return maas, maas_state
