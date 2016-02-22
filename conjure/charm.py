""" Charm utilities

Api for the charmstore:
https://github.com/juju/charmstore/blob/v4/docs/API.md
"""
import yaml
import requests
import os.path as path

cs = 'https://api.jujucharms.com/v4'


class CharmStoreException(Exception):
    """ CharmStore exception """


def get_bundle(bundle):
    """ Attempts to grab the bundle.yaml

    Arguments:
    bundle: name of bundle

    Returns:
    Dictionary of bundle's yaml
    """
    bundle = path.join(cs, bundle, 'archive/bundle.yaml')
    req = requests.get(bundle)
    if not req.ok:
        raise CharmStoreException("Problem getting bundle: {}".format(req))
    return yaml.safe_load(req.text)
