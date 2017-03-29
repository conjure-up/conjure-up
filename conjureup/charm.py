""" Charm utilities

Api for the charmstore:
https://github.com/juju/charmstore/blob/v5/docs/API.md
"""
import os.path as path

import requests
import yaml

cs = 'https://api.jujucharms.com/v5'
CHANNELS = ['stable', 'candidate', 'beta', 'edge']


def get_file(bundle, dst):
    """ Pulls a single file from the charmstore
    """
    bundle = path.join(cs, bundle, 'archive', dst)
    req = requests.get(bundle)
    if not req.ok:
        raise Exception("Could not query file in charmstore: {}".format(req))
    return req.text


def get_bundle(bundle_name, channel='stable'):
    """ Attempts to grab the bundle.yaml

    Arguments:
    bundle_name: name of bundle (ie canonical-kubernetes)
    channel: Which channel to pull the bundle from

    Returns:
    Dictionary of bundle's yaml unless to_file is True,
    then returns the path to the downloaded bundle
    """
    bundle_channel_info = get_channel_info(bundle_name, channel)
    bundle = "{}-{}".format(bundle_name,
                            bundle_channel_info['Revision'])
    return yaml.safe_load(get_file(bundle, 'bundle.yaml'))


def get_channel_info(bundle_name, channel='stable'):
    """ Grabs the channel information for a bundle

    Usage:
    https://api.jujucharms.com/charmstore/v5/canonical-kubernetes/meta/id?channel=edge

    Arguments:
    bundle_name: name of bundle (ie canonical-kubernetes)
    channel: the release channel (ie stable, candidate, beta, edge)
    """
    query = path.join(cs, bundle_name,
                      "meta/id?channel={}".format(channel))
    req = requests.get(query)
    if not req.ok:
        raise Exception(
            "Problem getting channel information: {}".format(req)
        )
    return req.json()


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
