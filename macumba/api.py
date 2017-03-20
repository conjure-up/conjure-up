import random
import requests
import string
import logging
import threading
import time
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit, urlunsplit
from .errors import (LoginError,
                     CharmNotFoundError,
                     ServerError,
                     RequestTimeout,
                     BadResponseError,
                     MacumbaError)
from .ws import JujuWS

log = logging.getLogger('macumba')


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
    charm_id = "{}/{}".format(series, charm)
    base_url = "https://api.jujucharms.com/charmstore/v5/meta/any?id={}"
    url = base_url.format(charm_id)
    r = requests.get(url)
    if r.status_code != 200:
        log.error("error accessing charm store API: '{}'".format(url))
        raise CharmNotFoundError("Unknown Error accessing Juju Charm Store")
    results = r.json()
    if len(results) == 0:
        raise CharmNotFoundError("Charm {} not found on Juju Charm"
                                 " Store.".format(charm))
    result = r.json()[charm_id]

    # ensure that series is in the charm Id:
    revno = result['Id'].split('-')[-1]
    result['Id'] = "cs:{}-{}".format(charm_id, revno)
    return result


class Base:
    """ Base api class
    """
    # define these in subclasses:
    API_VERSION = None
    CREDS_VERSION = None
    FACADE_VERSIONS = {}

    def __init__(self, url, password, user='user-admin', macaroons=None):
        """ init

        Params:
        url: URL in form of wss://{api-endpoint}/model/{uuid}/api
        password: Password for user
        user: juju user with access to endpoint
        """
        self.url = url
        self.password = password
        self.connlock = threading.RLock()
        with self.connlock:
            self.conn = JujuWS(url)

        if macaroons:
            user = ''
            password = ''

        nonce = ''.join(random.sample(string.printable, 12))
        self.creds = {'Type': 'Admin',
                      'Version': self.CREDS_VERSION,
                      'Request': 'Login',
                      'RequestId': 1,
                      'Params': {'auth-tag': user,
                                 'credentials': password,
                                 'nonce': nonce,
                                 'macaroons': macaroons or [],
                                 }}

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
            try:
                self.conn.do_connect()
                redirect_info = self._get_redirect_info()
                if redirect_info:
                    self._handle_redirect(redirect_info)
                else:
                    req_id = self.conn.do_send(self.creds)
                    res = self.receive(req_id)
                    if 'Error' in res:
                        raise LoginError(res['ErrorCode'])
            except Exception as e:
                raise
                raise LoginError(str(e))

    def _get_redirect_info(self):
        req_id = self.conn.do_send({
            "type": "Admin",
            "request": "RedirectInfo",
            "version": 3,
        })
        try:
            res = self.receive(req_id)
        except ServerError as e:
            if e.response['Error'] == 'not redirected':
                return None  # no redirect needed
            else:
                raise
        return res

    def _handle_redirect(self, redirect_info):
        url_parts = list(urlsplit(self.url))
        servers = [
            s for servers in redirect_info['servers']
            for s in servers if s['scope'] == 'public'
        ]
        with NamedTemporaryFile() as ca_certs:
            ssl_options = None
            if redirect_info['ca-cert']:
                ca_certs.write(
                    redirect_info['ca-cert'].encode('ascii'))
                ssl_options = {'ca_certs': ca_certs.name}
            for server in servers:
                self.conn.do_close()
                url_parts[1] = "{value}:{port}".format(**server)
                self.conn = JujuWS(urlunsplit(url_parts),
                                   ssl_options=ssl_options)
                self.conn.do_connect()
                try:
                    req_id = self.conn.do_send(self.creds)
                    try:
                        response = self.receive(req_id, timeout=5)
                    except RequestTimeout as e:
                        log.error(
                            'Connection to {value}:{port} timed out'.format(
                                **server))
                        continue  # try next server
                    except ServerError as e:
                        log.error(e.message)
                        continue  # try next server
                    if 'discharge-required-error' in response:
                        continue  # try next server
                    return response
                except Exception as e:
                    log.exception(e)
                    continue  # try next server
            else:
                raise LoginError('All redirect servers failed to login')

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
        if params['Type'] in self.FACADE_VERSIONS:
            params.update({'Version': self.FACADE_VERSIONS[params['Type']]})
        else:
            raise MacumbaError(
                'Unknown facade type: {}'.format(params['Type']))
        with self.connlock:
            req_id = self.conn.do_send(params)

        return self.receive(req_id, timeout)
