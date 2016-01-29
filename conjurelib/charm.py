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

Simple wrapper around theblues charmstore client

Api for the charmstore:
https://github.com/juju/charmstore/blob/v4/docs/API.md
"""
import os.path as path
import yaml
import requests
from theblues.charmstore import CharmStore

cs = CharmStore('https://api.jujucharms.com/v4')


class CharmStoreException(Exception):
    """ CharmStore exception """


def get_bundle(bundle):
    """ Attempts to grab the bundle.yaml

    Arguments:
    bundle: name of bundle

    Returns:
    Dictionary of bundle's yaml
    """
    archive_url = path.join(cs.archive_url(bundle), 'bundle.yaml')
    req = requests.get(archive_url)
    if not req.ok:
        raise CharmStoreException(
            "Unable to find bundle: RESP {}".format(req))
    return yaml.safe_load(req.text)
