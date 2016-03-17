""" Charm utilities

Api for the charmstore:
https://github.com/juju/charmstore/blob/v4/docs/API.md
"""
import yaml
import requests
import os.path as path
from tempfile import NamedTemporaryFile
from conjure.utils import FS
import q

cs = 'https://api.jujucharms.com/v4'


class CharmStoreException(Exception):
    """ CharmStore exception """


def get_bundle(bundle, to_file=False):
    """ Attempts to grab the bundle.yaml

    Arguments:
    bundle: name of bundle
    to_file: store to a temporary file

    Returns:
    Dictionary of bundle's yaml unless to_file is True,
    then returns the path to the downloaded bundle
    """
    bundle = path.join(cs, bundle, 'archive/bundle.yaml')
    q("Downloading bundle, ", bundle)
    req = requests.get(bundle)
    if not req.ok:
        raise CharmStoreException("Problem getting bundle: {}".format(req))
    if to_file:
        with NamedTemporaryFile(mode="w", encoding="utf-8",
                                delete=False) as tempf:
            FS.spew(tempf.name, req.text)
            return tempf.name
    else:
        return yaml.safe_load(req.text)
