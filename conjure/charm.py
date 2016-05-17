""" Charm utilities

Api for the charmstore:
https://github.com/juju/charmstore/blob/v5/docs/API.md
"""
import yaml
import requests
import os.path as path
from tempfile import NamedTemporaryFile
import shutil
from conjure.utils import spew

cs = 'https://api.jujucharms.com/v5'


def get_bundle(bundle, to_file=False):
    """ Attempts to grab the bundle.yaml

    Arguments:
    bundle: name of bundle or absolute path to local bundle
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

    bundle = path.join(cs, bundle, 'archive/bundle.yaml')
    req = requests.get(bundle)
    if not req.ok:
        raise Exception("Problem getting bundle: {}".format(req))
    if to_file:
        with NamedTemporaryFile(mode="w", encoding="utf-8",
                                delete=False) as tempf:
            spew(tempf.name, req.text)
            return tempf.name
    else:
        return yaml.safe_load(req.text)
