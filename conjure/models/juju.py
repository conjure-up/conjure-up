""" Represents a juju status """

from collections import Counter
import logging
import time

from conjure.models.machine import Machine
from conjure.models.service import Service

from macumba.errors import RequestTimeout

log = logging.getLogger('models.juju')


class JujuState:

    """ Represents a global Juju state """

    def __init__(self, juju):
        """ Builds a JujuState

        :param juju: Juju API connection
        """
        self.juju = juju
        self.start_time = time.time()
        self._juju_status = None
        self.valid_states = ['pending', 'started', 'down']

    def get_agent_states(self):
        """ Returns list of deployed services and their agent-state """
        states = []
        for svc in self.services:
            for unit in svc.units:
                states.append((svc.service_name, unit.agent_state))
        return states

    def all_agents_started(self):
        """ Check status of all deployed agents

        :param list svcs: List of services to check or empty for calling
                          service
        :rtype: :class:`~cloudinstall.service.Unit`
        :returns: True if all svcs are started, False otherwise
        """
        return all([state == "started" for _, state in
                    self.get_agent_states()])

    def status(self):
        """Returns juju status.
        Caches value for 20 seconds.

        Call invalidate_status_cache() to force next status call to
        fetch from server.

        If request times out (macumba default is 60 seconds), retries
        5 times.

        """
        elapsed_time = time.time() - self.start_time
        n_retries = 0
        if not self._juju_status or elapsed_time > 20:
            self._juju_status = None
            while self._juju_status is None:
                try:
                    self._juju_status = self.juju.status()
                except RequestTimeout:
                    n_retries += 1
                    if n_retries == 5:
                        raise Exception("Connection failure with juju API")
            self.start_time = time.time()
        return self._juju_status

    def invalidate_status_cache(self):
        """Invalidates cache of status.  Use this to force fetching from
        server more often than every 20 seconds.
        """
        self._juju_status = None

    def machines_summary(self):
        """ Returns summary of known machines and their status
        Excludes bootstrap.
        """
        m_status = self.status().get('Machines', {}).values()

        def get_info_string(m):
            s = m.get('AgentState')
            if s == '':
                s = 'unknown'
            si = m.get('AgentStateInfo')
            if si:
                s += " " + si
            l = m.get('Life', None)
            if l:
                s += " " + l
            return s

        d = Counter([get_info_string(m)
                     for m in m_status
                     if m['Id'] != '0'])
        return d

    def machine(self, machine_id):
        """ Return single machine state

        :param str machine_id: machine machine_id
        :returns: machine
        :rtype: :class:`~cloudinstall.machine.Machine`
        """
        for m in self.machines():
            if m.machine_id == machine_id:
                return m
        return Machine('-', {})

    def machines(self):
        """ Machines property

        :returns: machines known to juju (except bootstrap)
        :rtype: list
        """
        ret = self.status()
        machines = []

        for machine_id, machine in ret.get('Machines', {}).items():
            if '0' == machine_id:
                continue
            machines.append(Machine(machine_id, machine))
        return machines

    def machine_or_container(self, machine_id):
        """ returns machine or container matching the id
        """
        for machine in self.machines():
            if '0' == machine_id:
                continue
            if machine.machine_id == machine_id:
                return machine
            for container in machine.containers:
                if container.machine_id == machine_id:
                    return container
        return None

    def base_machine(self, machine_id):
        """ returns machine if given a numeric machine id,
        or machine hosting the container if given a container id
        """
        base_id = machine_id
        if 'lxc' in machine_id or 'kvm' in machine_id:
            base_id = machine_id.split('/')[0]
        return self.machine(base_id)

    def machines_allocated(self):
        """ Machines allocated property

        :returns: all machines in an allocated state (see self.valid_states)
        :rtype: list
        """
        return [m for m in self.machines()
                if m.agent_state in self.valid_states or
                (m.agent is not None and
                 m.agent['Status'] in self.valid_states)]

    def service(self, name):
        """ Return a single service entry

        :param str name: service/charm name
        :returns: a service entry or None
        :rtype: :class:`~cloudinstall.service.Service`
        """
        for s in self.services:
            if s.service_name == name:
                return s
        return Service(name, {})

    @property
    def services(self):
        """ Juju services property

        :returns: Service() of all loaded services
        :rtype: list
        """
        ret = self.status()
        services = []

        for name, service in ret.get('Services', {}).items():
            services.append(Service(name, service))

        return services

    @property
    def networks(self):
        """ Juju netwoks property
        """
        return self.status()['Networks']
