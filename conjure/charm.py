# Copyright (c) 2015 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Charm utilities


Api for the charmstore:
https://github.com/juju/charmstore/blob/v4/docs/API.md

Example api call for checking what bundles contain a
specific charm (hadoop in this case):
https://api.jujucharms.com/charmstore/v4/hadoop/meta/bundles-containing


"""
import os.path as path
import requests
import logging

log = logging.getLogger('charm')


class CharmNotFoundError(Exception):
    """ Exception in querying charmstore
    """
    pass


def query_cs(endpoint):
    """ This helper routine will query the charm store to pull latest revisions
    and charmstore url for the api.

    Arguments:
    endpoint: api endpoint, eg ~adam-stokes/ghost/meta/id
    """
    charm_store_url = 'https://api.jujucharms.com/v4/'
    url = path.join(charm_store_url, endpoint)
    r = requests.get(url)
    if r.status_code != 200:
        log.error("could not find charm store URL for charm '{}'".format(url))
        rj = r.json()
        raise CharmNotFoundError("{type} {charm_id}".format(**rj))

    return r.json()


class CharmMeta:
    def __init__(self, charm, series="trusty"):
        """ init

        Arguments:
        charm: Name of charm
        series: Ubuntu series, defaults: trusty
        """
        self.charm = charm
        self.series = series
        self.meta_path = path.join(self.series, self.charm, 'meta')

    def config(self):
        """ Charm Config

        Returns:
        Charm configuration specification as stored in its config.yaml
        """
        endpoint = path.join(self.meta_path, 'charm-config')
        res = query_cs(endpoint)
        return res['Options']

    def id(self):
        """ Charm ID

        Returns:
        Charm ID
        """
        endpoint = path.join(self.meta_path, 'id')
        res = query_cs(endpoint)
        return res

    def metadata(self):
        """ Metadata

        Returns:
        Metadata about the charm, summary, description, etc.
        """
        endpoint = path.join(self.meta_path, 'charm-metadata')
        res = query_cs(endpoint)
        return res
