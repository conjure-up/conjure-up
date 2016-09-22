""" Charm utilities

Api for the charmstore:
https://github.com/juju/charmstore/blob/v5/docs/API.md
"""
import os.path as path
import shutil
from tempfile import NamedTemporaryFile

import requests
import yaml

cs = 'https://api.jujucharms.com/v5'


def get_file(bundle, dst):
    """ Pulls a single file from the charmstore
    """
    bundle = path.join(cs, bundle, 'archive', dst)
    req = requests.get(bundle)
    if not req.ok:
        raise Exception("Could not query file in charmstore: {}".format(req))
    return req.json()


def get_bundle(bundle, to_file=False):
    """ Attempts to grab the bundle.yaml

    Arguments:
    bundle: URL of bundle or absolute path to local bundle
    to_file: store to a temporary file

    Returns:
    Dictionary of bundle's yaml unless to_file is True,
    then returns the path to the downloaded bundle
    """
    if path.isfile(bundle):
        if to_file:
            with NamedTemporaryFile(mode="w", encoding="utf-8",
                                    delete=False) as tempf:
                shutil.copyfile(bundle, tempf.name)
            return tempf.name
        else:
            with open(bundle) as f:
                return yaml.safe_load(f.read())

    req = requests.get(bundle)
    if not req.ok:
        raise Exception("Problem getting bundle: {}".format(req))
    if to_file:
        with NamedTemporaryFile(mode="w", encoding="utf-8",
                                delete=False) as tempf:
            tempf.write(req.text)
            return tempf.name
    else:
        return yaml.safe_load(req.text)


def search(tags, promulgated=True):
    """ Search charmstore by tag(s)

    Usage:
    https://api.jujucharms.com/charmstore/v5/search?tags=conjure-up-openstack
    &include=id&include=extra-info/conjure-up&type=bundle

    Arguments:
    tags: single or list of tags to search for
    promulgated: search only blessed bundles
    """
    if not isinstance(tags, list):
        tags = [tags]

    tags = ["conjure-up-{}".format(t) for t in tags]
    query_str = "&tags=".join(tags)
    if promulgated:
        query_str += "&promulgated=1"
    query_str += "&include=bundle-metadata"
    query_str += "&include=id"
    query_str += "&include=extra-info/conjure-up"
    query_str += "&type=bundle"
    query = path.join(cs, 'search?tags={}'.format(query_str))
    req = requests.get(query)
    if not req.ok:
        raise Exception(
            "Problem getting tagged bundles: {}".format(req))
    return req.json()
