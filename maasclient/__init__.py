#
# client.py - Client routines for MAAS API
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

import bson
from requests_oauthlib import OAuth1
import requests
import json


class MaasClient:

    """ Client Class
    """

    def __init__(self, auth):
        """ Entry point to client routines for interfacing
        with MAAS api.

        :param auth: MAAS Authorization class (required)
        """
        self.auth = auth

    def _oauth(self):
        """ Generates OAuth attributes for protected resources

        :returns: OAuth class
        """
        oauth = OAuth1(self.auth.consumer_key,
                       client_secret=self.auth.consumer_secret,
                       resource_owner_key=self.auth.token_key,
                       resource_owner_secret=self.auth.token_secret,
                       signature_method='PLAINTEXT',
                       signature_type='query')
        return oauth

    def get(self, url, params=None):
        """ Performs a authenticated GET against a MAAS endpoint

        :param url: MAAS endpoint
        :param params: extra data sent with the HTTP request
        """
        return requests.get(url=self.auth.api_url + url,
                            auth=self._oauth(),
                            params=params)

    def post(self, url, params=None):
        """ Performs a authenticated POST against a MAAS endpoint

        :param url: MAAS endpoint
        :param params: extra data sent with the HTTP request
        """
        return requests.post(url=self.auth.api_url + url,
                             auth=self._oauth(),
                             data=params)

    def delete(self, url, params=None):
        """ Performs a authenticated DELETE against a MAAS endpoint

        :param url: MAAS endpoint
        :param params: extra data sent with the HTTP request
        """
        return requests.delete(url=self.auth.api_url + url,
                               auth=self._oauth())

    ###########################################################################
    # Boot Images API
    ###########################################################################
    def boot_images(self, uuid):
        """ Query boot images list

        :param str uuid: uuid of cluster
        :returns: list of boot images
        :rtype: list
        """
        _url = "/nodegroups/{uuid}/boot-images/".format(uuid=uuid)
        res = self.get(_url)
        if res.ok:
            return json.loads(res.text)
        return []

    def import_boot_images(self):
        """ Import boot images on all accepted controllers

        :returns: true on success, false on failure
        :rtype: bool
        """
        _url = "/nodegroups/"
        res = self.post(_url, dict(op='import_boot_images'))
        if res.ok:
            return True
        return False

    def report_boot_images(self, uuid):
        """ Describe imported images

        :param str uuid: uuid of cluster
        :returns: information on import images
        :rtype: dict
        """
        _url = "/nodegroups/{uuid}/boot-images".format(uuid=uuid)
        res = self.post(_url, dict(op='report_boot_images'))
        if res.ok:
            return json.loads(res.text)
        return {}

    ###########################################################################
    # Node API
    ###########################################################################
    @property
    def nodes(self):
        """ Nodes managed by MAAS

        :returns: managed nodes
        :rtype: list
        """
        res = self.get('/nodes/', dict(op='list'))
        if res.ok:
            return json.loads(res.text)
        return []

    def nodes_V2(self, **params):
        """ Nodes managed by MAAS

        See http://maas.ubuntu.com/docs/api.html#nodes

        :param params: keyword parameters to filter returned nodes
                       allowed values include hostnames, mac_addresses,
                       zone.
        :returns: managed nodes
        :rtype: list
        """
        params['op'] = 'list'
        res = self.get('/nodes/', params)
        if res.ok:
            machines = map(Machine, res.json())
            # Filter by state post response manually till maas fixes.
            if 'state' in params:
                machines = [m for m in machines if m.state == params['state']]
            return machines
        return []

    def node_get(self, node_id):
        res = self.get('/nodes/%s' % node_id)
        if res.ok:
            return Machine(res.json())
        return None

    def node_acquire(self, **params):
        """
        See http://maas.ubuntu.com/docs/api.html#nodes
        """
        params['op'] = 'acquire'
        res = self.post('/nodes/', params)
        if res.ok:
            return Machine(res.json())
        return []

    def node_release(self, node_id):
        """ Release a node back into the pool.
        """
        res = self.post('/nodes/%s/' % node_id, {'op': 'release'})
        return res.ok

    def node_start(self, node_id, user_data=None, distro_series=None):
        """ Power up a node

        :param node_id: machine identification
        :returns: True on success False on failure
        """
        params = {'op': 'start'}
        if user_data:
            params['user_data'] = user_data
        if distro_series:
            params['distro_series'] = distro_series
        res = self.post('/nodes/%s/' % node_id, params)
        return res.ok

    def node_stop(self, node_id):
        """ Shutdown a node

        :param node_id: machine identification
        :returns: True on success False on failure
        """
        res = self.post('/nodes/%s/' % node_id, {'op': 'stop'})
        return res.ok

    def node_details(self, system_id):
        """ Node Details from e.g. lshw.
        May be encoded as XML.

        :returns: dictionary of commissioning details
        :rtype: dict
        """
        res = self.get('/nodes/{}/'.format(system_id),
                       dict(op='details'))
        if res.ok:
            ds = bson.decode_all(res.content)
            if len(ds) == 0:
                return None
            return ds[0]
        return None

    def nodes_accept_all(self):
        """ Accept all commissioned nodes

        :returns: Status
        :rtype: bool
        """

        res = self.post('/nodes/', dict(op='accept_all'))
        if res.ok:
            return True
        return False

    def node_commission(self, system_id):
        """ (Re)commission a node

        :param system_id: machine identification
        :returns: True on success False on failure
        """
        res = self.post('/nodes/%s' % (system_id,), dict(op='commission'))
        if res.ok:
            return True
        return False

    def node_remove(self, system_id):
        """ Delete a node

        :param system_id: machine identification
        :returns: True and success False on failure
        """
        res = self.delete('/nodes/%s' % (system_id,))
        if res.ok:
            return True
        return False

    ###########################################################################
    # Nodegroups API
    ###########################################################################
    @property
    def nodegroups(self):
        """ List nodegroups

        :returns: List of nodegroups
        :rtype list:
        """
        res = self.get('/nodegroups/', dict(op='list'))
        if res.ok:
            return json.loads(res.text)
        return []

    def nodegroups_download_progress(self, uuid):
        """ Report download progress for a cluster controller

        :param str uuid: uuid of controller
        :returns: file information
        :rtype: dict
        """
        _url = "/nodegroups/{uuid}/".format(uuid=uuid)
        res = self.post(_url, dict(op='report_download_progress'))
        if res.ok:
            return json.loads(res.text)
        return {}

    ###########################################################################
    # Tag API
    ###########################################################################
    @property
    def tags(self):
        """ List tags known to MAAS

        :returns: List of tags or empty list
        """
        res = self.get('/tags/', dict(op='list'))
        if res.ok:
            return json.loads(res.text)
        return []

    def tag_new(self, tag):
        """ Create tag if it doesn't exist.

        :param tag: Tag name
        :returns: Success/Fail boolean
        """
        tags = {tagmd['name'] for tagmd in self.tags}
        if tag not in tags:
            res = self.post('/tags/', dict(op='new', name=tag))
            return res.ok
        return False

    def tag_delete(self, tag):
        """ Delete a tag

        :param tag: tag id
        :type tag: str
        :returns: True on success False on failure
        :rtype: bool
        """
        res = self.delete('/tags/%s' % (tag,))
        if res.ok:
            return True
        return False

    def tag_machine(self, tag, system_id):
        """ Tag the machine with the specified tag.

        :param tag: Tag name
        :type tag: str
        :param system_id: ID of node
        :type system_id: str
        :returns: Success or Fail
        :rtype: bool
        """

        # Make use of rest api
        res = self.post('/tags/%s/' % (tag,),
                        dict(op='update_nodes',
                             add=system_id))
        if res.ok:
            return True
        return False

    def tag_name(self, nodes):
        """ Tag each managed node with its hostname.

        This is a bit ugly. Since we want to be able to juju deploy to
        a particular node that the user has selected, we use juju's
        constraints support for maas. Unfortunately, juju didn't
        implement maas-name directly, we have to tag each node with
        its hostname for now so that we can pass that tag as a
        constraint to juju.

        """
        for machine in nodes:
            system_id = machine['system_id']
            if 'tag_names' not in machine['tag_names'] or \
               system_id not in machine['tag_names']:
                self.tag_new(system_id)
                self.tag_machine(system_id, system_id)

    def tag_fpi(self, nodes):
        """ Tag each DECLARED host with the FPI tag.

        Also a little strange: we could define a tag with
        'definition=true()' and automatically tag each node. However,
        each time we un-tag a node, maas evaluates the xpath
        expression again and re-tags it. So, we do it once, manually,
        when the machine is in the DECLARED state (also to avoid
        re-tagging things that have already been tagged).

        :param maas: MAAS object representing all managed nodes
        """
        FPI_TAG = 'use-fastpath-installer'
        self.tag_new(FPI_TAG)
        for machine in nodes:
            if machine['status'] == 0:
                self.tag_machine(FPI_TAG, machine['system_id'])

    ###########################################################################
    # Users API
    ###########################################################################
    @property
    def users(self):
        """ List users on MAAS

        :returns: List of registered users or an empty list
        """
        res = self.get('/users/')
        if res.ok:
            return json.loads(res.text)
        return []

    ##########################################################################
    # Network API
    ##########################################################################
    @property
    def networks(self):
        """ List networks
        :returns: List of networks
        """
        res = self.get('/networks/')
        if res.ok:
            return res.json()
        return []

    ###########################################################################
    # Zone API
    ###########################################################################
    @property
    def zones(self):
        """ List physical zones

        :returns: List of managed zones or empty list
        """
        res = self.get('/zones/')
        if res.ok:
            return json.loads(res.text)
        return []

    def zone_new(self, name, description="Zone created by API"):
        """ Create a physical zone

        :param name: Name of the zone
        :param description: Description of zone.
        :returns: True on success False on failure
        """
        res = self.post('/zones/', dict(name=name,
                                        description=description))
        if res.ok:
            return True
        return False

    def zone_delete(self, name):
        """ Delete a zone.

        :param name: Name of the zone to be deleted
        :returns: True on success & False on failure.
        """
        res = self.delete('/zones/{}/'.format(name))
        return res.ok


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
