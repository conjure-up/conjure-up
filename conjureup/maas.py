""" simple maas client
"""

import requests
from requests_oauthlib import OAuth1
from enum import Enum
import time

from conjureup.app_config import app
from conjureup.async import submit
from conjureup.units import human_to_mb
from conjureup import juju


class MaasClient:
    API_VERSION = '2.0'
    CACHE = {}

    def __init__(self, server_address, consumer_key,
                 token_key, token_secret):
        """

        Arguments:
        server_address: maas server ip/hostname
        consumer_key: maas consumer key for authenticated maas user
        token_key: user token
        token_secret: user token secret
        """
        self.api_url = "http://{}:5240/MAAS/api/{}".format(server_address,
                                                           self.API_VERSION)
        self.oauth = OAuth1(consumer_key,
                            resource_owner_key=token_key,
                            resource_owner_secret=token_secret,
                            signature_method='PLAINTEXT')

    def _prepare_url(self, url):
        if not url.endswith('/'):
            url = url + '/'
        return self.api_url + url

    def get(self, url, params=None):
        """ Performs a authenticated GET against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.get(url=self._prepare_url(url),
                            headers={'Accept': 'application/json'},
                            auth=self.oauth,
                            params=params)

    def post(self, url, params=None):
        """ Performs a authenticated POST against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.post(url=self._prepare_url(url),
                             headers={'Accept': 'application/json'},
                             auth=self.oauth,
                             data=params)

    def put(self, url, params=None):
        """ Performs a authenticated PUT against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.put(url=self._prepare_url(url),
                            headers={'Accept': 'application/json'},
                            auth=self.oauth,
                            data=params)

    def delete(self, url, params=None):
        """ Performs a authenticated DELETE against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.delete(url=self._prepare_url(url),
                               headers={'Accept': 'application/json'},
                               auth=self.oauth)

    # Higher level API
    def _get_machines_async(self):
        r = self.get("/machines/")
        if r.status_code != 200:
            raise Exception("Error in MAAS API")
        return [MaasMachine(d) for d in r.json()]

    def _update_machine_cache(self, future):
        val = future.result()
        self.CACHE['machines'] = (val, time.time())

    def get_machines(self):
        """cached API call, refreshes in background every 5 sec

        returns None on the first call so you know it's just loading
        instead of an actual empty list of machines.

        """
        now = time.time()
        c_val, c_ts = self.CACHE.get('machines', (None, now))
        if c_val is None or now - c_ts > 5:
            f = submit(self._get_machines_async,
                       lambda _: None)
            f.add_done_callback(self._update_machine_cache)

        return c_val


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


class MaasMachine:
    """ Single maas machine """

    def __init__(self, machine):
        self.machine = machine

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
            _storage_in_gb = float(self.machine.get('storage')) / 1024
        except ValueError:
            return "N/A"
        return "{size:.1f} G".format(size=_storage_in_gb)

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
            _mem = float(self.machine.get('memory'))
        except ValueError:
            return "N/A"
        if _mem > 1024:
            _mem = _mem / 1024
            return "{:.1f} G".format(_mem)
        else:
            return "{:.1f} M".format(_mem)

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
        return "<MaasMachine({dns_name},{mem}," \
            "{storage},{cpus})>".format(dns_name=self.hostname,
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


def setup_maas():
    try:
        maascreds = juju.get_credentials()['maas'][app.current_controller]
    except KeyError:
        raise Exception("Could not get credentials for "
                        "maas controller {}".format(app.current_controller))

    bc = juju.get_bootstrap_config(app.current_controller)
    endpoint = bc.get('endpoint', None)
    if endpoint is None:
        raise Exception("Couldn't find endpoint for controller".format(
            app.current_controller))

    api_key = maascreds['maas-oauth']
    try:
        consumer_key, token_key, token_secret = api_key.split(':')
    except:
        raise Exception("Could not parse MAAS API Key '{}'".format(api_key))

    app.maas.client = MaasClient(server_address=endpoint,
                                 consumer_key=consumer_key,
                                 token_key=token_key,
                                 token_secret=token_secret)


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
