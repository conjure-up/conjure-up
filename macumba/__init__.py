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

from ws4py.client.threadedclient import WebSocketClient
import json
import logging
import requests
from os import path
from queue import Queue, Empty
import pprint
import threading
import time

log = logging.getLogger('macumba')

creds = {'Type': 'Admin',
         'Request': 'Login',
         'RequestId': 1,
         'Params': {'AuthTag': 'user-admin',
                    'Password': None}}


class MacumbaError(Exception):

    "Base error class"


class CharmNotFoundError(MacumbaError):

    "Error when getting charm store url"


def query_cs(charm):
    """ This helper routine will query the charm store to pull latest revisions
    and charmstore url for the api.

    :param str charm: charm name, can be in the form of 'precise/<charm>' to
                      specify an alternate series.
    """
    try:
        series, charm = charm.split('/')
    except ValueError:
        series = 'trusty'
    charm_store_url = 'https://manage.jujucharms.com/api/3/charm'
    url = path.join(charm_store_url, series, charm)
    r = requests.get(url)
    if r.status_code != 200:
        log.error("could not find charm store URL for charm '{}'".format(url))
        rj = r.json()
        raise CharmNotFoundError("{type} {charm_id}".format(**rj))

    return r.json()


class PrettyLog():

    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return pprint.pformat(self.obj)


class Jobs:
    HostUnits = "JobHostUnits"
    ManageEnviron = "JobManageEnviron"
    ManageState = "JobManageState"


class LoginError(MacumbaError):

    "Error logging in to juju api"


class ServerError(MacumbaError):

    "Generic error response from server"

    def __init__(self, message, response):
        self.response = response
        super().__init__(self, message)


class BadResponseError(MacumbaError):

    "Unable to parse response from server"


class ConnectionClosedError(MacumbaError):

    "Attempted to receive messages from closed connection"


class UnknownRequestError(MacumbaError):

    "Attempted to receive a message with an unknown ID"


class RequestTimeout(MacumbaError):

    "Request timed out"


class JujuWS(WebSocketClient):

    def __init__(self, url, password, protocols=['https-only'],
                 extensions=None, ssl_options=None, headers=None,
                 start_reqid=1):
        WebSocketClient.__init__(self, url, protocols, extensions,
                                 ssl_options=ssl_options, headers=headers)
        self.open_done = threading.Event()
        self.rid_lock = threading.RLock()
        self.msglock = threading.RLock()
        self.messages = {}
        self._cur_request_id = start_reqid

    # WebSocketClient subclass overrides, run in private thread:
    def opened(self):
        self.open_done.set()

    def received_message(self, m):
        msg = json.loads(m.data.decode('utf-8'))
        msg_req_id = msg['RequestId']
        with self.msglock:
            self.messages[msg_req_id] = msg

    def closed(self, code, reason=None):
        log.debug("socket closed: code:{} reason:{}".format(code, reason))

    # actions for users of the class:
    def get_current_request_id(self):
        "only intended to pass to constructor of a replacing client"
        return self._cur_request_id

    def do_close(self):
        self.close()

    def do_connect(self):
        self.connect()
        self.open_done.wait()
        self.open_done.clear()
        rv = self.do_send(creds)
        return rv

    def do_send(self, json_message):
        with self.rid_lock:
            self._cur_request_id += 1
            request_id = self._cur_request_id

        json_message['RequestId'] = request_id

        self.send(json.dumps(json_message))

        with self.msglock:
            self.messages[request_id] = None

        return request_id

    def do_receive(self, request_id):
        """Checks for message matching request_id.

        Will return None if message has not arrived yet.

        Raises UnknownRequestError if request_id hasn't been sent yet
        (or was already received).

        """
        if self.terminated:
            raise ConnectionClosedError

        with self.msglock:
            if request_id not in self.messages:
                errmsg = ("{} not in messages. "
                          "cur = {}".format(request_id,
                                            self._cur_request_id))
                raise UnknownRequestError(errmsg)

            message = self.messages[request_id]
            if message is not None:
                del self.messages[request_id]

        return message


class JujuClient:

    def __init__(self, url='wss://localhost:17070', password='pass'):
        self.url = url
        self.password = password
        self.connlock = threading.RLock()
        with self.connlock:
            self.conn = JujuWS(url, password)
        creds['Params']['Password'] = password

    def _prepare_strparams(self, d):
        r = {}
        for k, v in d.items():
            r[k] = str(v)
        return r

    def _prepare_constraints(self, constraints):
        for k in ['cpu-cores', 'cpu-power', 'mem', 'root-disk']:
            if constraints.get(k):
                constraints[k] = int(constraints[k])
        return constraints

    def login(self):
        """Connect and log in to juju websocket endpoint.
        
        block other threads until done.
        """
        with self.connlock:
            req_id = self.conn.do_connect()
            try:
                res = self.receive(req_id)
                if 'Error' in res:
                    raise LoginError(res['ErrorCode'])
            except Exception as e:
                raise LoginError(str(e))

    def reconnect(self):
        with self.connlock:
            self.close()
            start_id = self.conn.get_current_request_id() + 1
            self.conn = JujuWS(self.url,
                               self.password,
                               start_reqid=start_id)
            self.login()

    def close(self):
        """ Closes connection to juju websocket """
        with self.connlock:
            self.conn.do_close()

    def receive(self, request_id, timeout=None):
        """receives expected message.
        
        returns parsed response object.

        if timeout is set, raises RequestTimeout after 'timeout' seconds
        with no received message.

        """
        res = None
        start_time = time.time()
        while res is None:
            with self.connlock:
                res = self.conn.do_receive(request_id)
            if res is None:
                time.sleep(0.1)
                if timeout and (time.time() - start_time > timeout):
                    raise RequestTimeout(request_id)

        if 'Error' in res:
            raise ServerError(res['Error'], res)

        try:
            return res['Response']
        except:
            raise BadResponseError("Failed to parse response: {}".format(res))

    def call(self, params, timeout=None):
        """ Get json data from juju api daemon.

        :params params: Additional params to be passed into request
        :type params: dict
        """
        with self.connlock:
            req_id = self.conn.do_send(params)

        return self.receive(req_id, timeout)

    def info(self):
        """ Returns Juju environment state """
        return self.call(dict(Type="Client",
                              Request="EnvironmentInfo"))

    def status(self):
        """ Returns status of juju environment """
        return self.call(dict(Type="Client",
                              Request="FullStatus"),
                         timeout=60)

    def get_watcher(self):
        """ Returns watcher """
        return self.call(dict(Type="Client",
                              Request="WatchAll"))

    def get_watched_tasks(self, watcher_id):
        """ Returns a list of all watches for Id """
        return self.call(dict(Type="AllWatcher",
                              Request="Next",
                              Id=watcher_id))

    def add_charm(self, charm_url):
        """ Adds charm """
        return self.call(dict(Type="Client",
                              Request="AddCharm",
                              Params=dict(URL=charm_url)))

    def get_charm(self, charm_url):
        """ Get charm """
        return self.call(dict(Type='Client',
                              Request='CharmInfo',
                              Params=dict(CharmURL=charm_url)))

    def get_env_constraints(self):
        """ Get environment constraints """
        return self.call(dict(Type="Client",
                              Request="GetEnvironmentConstraints"))

    def set_env_constraints(self, constraints):
        """ Set environment constraints """
        return self.call(dict(Type="Client",
                              Request="SetEnvironmentConstraints",
                              Params=constraints))

    def get_env_config(self):
        """ Get environment config """
        return self.call(dict(Type="Client",
                              Request="EnvironmentGet"))

    def set_env_config(self, config):
        """ Sets environment config variables """
        return self.call(dict(Type="Client",
                              Request="EnvironmentSet",
                              Params=dict(Config=config)))

    def add_machine(self, series="", constraints={},
                    machine_spec="", parent_id="", container_type=""):
        """Allocate a new machine from the iaas provider.
        """
        if machine_spec:
            err_msg = "Cant specify machine spec with container_type/parent_id"
            assert not (parent_id or container_type), err_msg
            parent_id, container_type = machine_spec.split(":", 1)

        params = dict(
            Series=series,
            ContainerType=container_type,
            ParentId=parent_id,
            Constraints=self._prepare_constraints(constraints),
            Jobs=[Jobs.HostUnits])
        return self.add_machines([params])

    def add_machines(self, machines):
        """ Add machines """
        return self.call(dict(Type="Client",
                              Request="AddMachines",
                              Params=dict(MachineParams=machines)))

    def destroy_machines(self, machine_ids, force=False):
        params = {"MachineNames": machine_ids}
        if force:
            params["Force"] = True
        return self.call(dict(Type="Client",
                              Request="DestroyMachines",
                              Params=params))

    def add_relation(self, endpoint_a, endpoint_b):
        """ Adds relation between units """
        try:
            rv = self.call(dict(Type="Client",
                                Request="AddRelation",
                                Params=dict(Endpoints=[endpoint_a,
                                                       endpoint_b])))
        except ServerError as e:
            # do not treat pre-existing relations as exceptions:
            if 'relation already exists' in e.response['Error']:
                rv = e.response
            else:
                raise e

        return rv

    def remove_relation(self, endpoint_a, endpoint_b):
        """ Removes relation """
        return self.call(dict(Type="Client",
                              Request="DestroyRelaiton",
                              Params=dict(Endpoints=[endpoint_a,
                                                     endpoint_b])))

    def deploy(self, charm, service_name, num_units=1, config_yaml="",
               constraints=None, machine_spec=""):
        """ Deploy a charm to an instance

        :param str charm: Name of charm
        :param str service_name: name of service
        :param int num_units: number of units
        :param str config_yaml: charm configuration options
        :param dict constraints: deploy constraints
        :param str machine_spec: Type of machine to deploy to
        :returns: Deployed charm status
        """
        params = {'ServiceName': service_name}

        _url = query_cs(charm)
        params['CharmUrl'] = _url['charm']['url']
        params['NumUnits'] = num_units
        params['ConfigYAML'] = config_yaml

        if constraints:
            params['Constraints'] = self._prepare_constraints(
                constraints)
        if machine_spec:
            params['ToMachineSpec'] = machine_spec
        return self.call(dict(Type="Client",
                              Request="ServiceDeploy",
                              Params=dict(params)))

    def set_config(self, service_name, config_keys):
        """ Sets machine config """
        return self.call(dict(Type="Client",
                              Request="ServiceSet",
                              Params=dict(ServiceName=service_name,
                                          Options=config_keys)))

    def unset_config(self, service_name, config_keys):
        """ Unsets machine config """
        return self.call(dict(Type="Client",
                              Request="ServiceUnset",
                              Params=dict(ServiceName=service_name,
                                          Options=config_keys)))

    def set_charm(self, service_name, charm_url, force=0):
        return self.call(dict(Type="Client",
                              Request="ServiceSetCharm",
                              Params=dict(ServiceName=service_name,
                                          CharmUrl=charm_url,
                                          Force=force)))

    def get_service(self, service_name):
        """ Get charm, config, constraits for srevice"""
        return self.call(dict(Type="Client",
                              Request="ServiceGet",
                              Params=dict(ServiceName=service_name)))

    def get_config(self, service_name):
        """ Get service configuration """
        svc = self.get_service(service_name)
        return svc['Config']

    def get_constraints(self, service_name):
        """ Get service constraints """
        return self.call(dict(Type="Client",
                              Request="GetServiceConstraints",
                              Params=dict(ServiceName=service_name)))

    def set_constraints(self, service_name, constraints):
        """ Sets service level constraints """
        return self.call(dict(Type="Client",
                              Request="SetServiceConstraints",
                              Params=dict(ServiceName=service_name,
                                          Constraints=constraints)))

    def update_service(self, service_name, charm_url, force_charm_url=0,
                       min_units=1, settings={}, constraints={}):
        """ Update service """
        return self.call(dict(Type="Client",
                              Request="SetServiceConstraints",
                              Params=dict(ServiceName=service_name,
                                          CharmUrl=charm_url,
                                          MinUnits=min_units,
                                          SettingsStrings=settings,
                                          Constraints=constraints)))

    def destroy_service(self, service_name):
        """ Destroy a service """
        return self.call(dict(Type="Client",
                              Request="ServiceDestroy",
                              Params=dict(ServiceName=service_name)))

    def expose(self, service_name):
        """ Expose a service """
        return self.call(dict(Type="Client",
                              Request="ServiceExpose",
                              Params=dict(ServiceName=service_name)))

    def unexpose(self, service_name):
        """ Unexpose service """
        return self.call(dict(Type="Client",
                              Request="ServiceUnexpose",
                              Params=dict(ServiceName=service_name)))

    def valid_relation_name(self, service_name):
        """ All possible relation names for service """
        return self.call(dict(Type="Client",
                              Request="ServiceCharmRelations",
                              Params=dict(ServiceName=service_name)))

    def add_unit(self, service_name, num_units=1, machine_spec=""):
        """ Add unit

        :param str service_name: Name of charm
        :param int num_units: Number of units
        :param str machine_spec: Type of machine to deploy to
        :returns dict: Units added
        """
        params = {}
        params['ServiceName'] = service_name
        params['NumUnits'] = num_units
        if machine_spec:
            params['ToMachineSpec'] = machine_spec

        return self.call(dict(Type="Client",
                              Request="AddServiceUnits",
                              Params=dict(params)))

    def remove_unit(self, unit_names):
        """ Removes unit """
        return self.call(dict(Type="Client",
                              Request="DestroyServiceUnits",
                              Params=dict(UnitNames=unit_names)))

    def resolved(self, unit_name, retry=0):
        """ Resolved """
        return self.call(dict(Type="Client",
                              Request="Resolved",
                              Params=dict(UnitName=unit_name,
                                          Retry=retry)))

    def get_public_address(self, target):
        """ Gets public address of instance """
        return self.call(dict(Type="Client",
                              Request="PublicAddress",
                              Params=dict(Target=target)))

    def set_annotations(self, entity, entity_type, annotation):
        """ Sets annotations.
        :param dict annotation: dict with string pairs.
        """
        return self.call(dict(Type="Client",
                              Request="SetAnnotations",
                              Params=dict(Tag="%s-%s" % (entity_type, entity),
                                          Pairs=annotation)))

    def get_annotations(self, entity, entity_type):
        """ Gets annotations """
        return self.call(dict(Type="Client",
                              Request="GetAnnotations",
                              Params=dict(Tag="%s-%s" % (entity_type,
                                                         entity))))
