""" simple maas client
"""

from requests_oauthlib import OAuth1
import requests


class MaasClient:
    API_VERSION = '2.0'

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

    def get(self, url, params=None):
        """ Performs a authenticated GET against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        print(self.api_url + url)
        return requests.get(url=self.api_url + url,
                            auth=self.oauth,
                            params=params)

    def post(self, url, params=None):
        """ Performs a authenticated POST against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.post(url=self.api_url + url,
                             auth=self.oauth,
                             data=params)

    def put(self, url, params=None):
        """ Performs a authenticated PUT against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.put(url=self.api_url + url,
                            auth=self.oauth,
                            data=params)

    def delete(self, url, params=None):
        """ Performs a authenticated DELETE against a MAAS endpoint

        Arguments:
        url: MAAS endpoint
        params: extra data sent with the HTTP request
        """
        return requests.delete(url=self.api_url + url,
                               auth=self.oauth)


class vocab(dict):
    __slots__ = ()

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            return AttributeError(k)

    def label(self, value):
        for k, v in self.items():
            if v == value:
                return k

MAAS_STATES = vocab(
    DECLARED=0,
    COMMISSIONING=1,
    FAILED_TESTS=2,
    MISSING=3,
    READY=4,
    RESERVED=5,
    ALLOCATED=6,
    RETIRED=7)


class Machine(dict):

    __slots__ = ()

    @property
    def hostname(self):
        return self['hostname']

    @property
    def arch(self):
        return self['architecture']

    @property
    def status(self):
        return self['status']

    @property
    def cpu_cores(self):
        return self['cpu_count']

    @property
    def mem(self):
        """ Size Memory in mb"""
        return self['memory']

    @property
    def disk(self):
        """ Size root disk in gb"""
        return self['storage']

    @property
    def system_id(self):
        return self['system_id']

    @property
    def tags(self):
        return self.get('tags', [])

    @property
    def ip_addresses(self):
        return self['ip_addresses']

    @property
    def mac_addresses(self):
        return [m['mac_address'] for m in self.get('macaddress_set', [])]

    @property
    def status_label(self):
        return MAAS_STATES.label(self.status)
