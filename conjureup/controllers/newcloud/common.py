import os
import os.path as path
from subprocess import DEVNULL, CalledProcessError

import yaml
from pkg_resources import parse_version

from conjureup import controllers, utils
from conjureup.app_config import app

cred_path = path.join(utils.juju_path(), 'credentials.yaml')


def __format_creds(creds):
    """ Formats the credentials into strings from the widgets values
    """
    formatted = {}
    for field in creds['fields']:
        if not field['storable']:
            continue
        if 'storable-as' in field:
            if isinstance(field['storable-as'], list):
                formatted[field['key']] = [field['input'].value]
        formatted[field['key']] = field['input'].value
    return formatted


def try_get_creds(cloud):
    """ Check if credentials for existing cloud already exists so
    we can bypass the cloud config view and go straight to bootstrapping

    Arguments:
    cloud: public cloud

    Returns:
    First set of credentials found for cloud
    """
    if not path.isfile(cred_path):
        return None

    existing_creds = yaml.safe_load(open(cred_path))
    if 'credentials' not in existing_creds:
        return None

    if cloud not in existing_creds['credentials'].keys():
        return None

    if len(existing_creds['credentials'][cloud].keys()) == 0:
        return None

    for k in existing_creds['credentials'][cloud].keys():
        if 'default-region' in k:
            continue
        else:
            return k


def save_creds(cloud, credentials):
    """ stores credentials for cloud
    """
    try:
        existing_creds = yaml.safe_load(open(cred_path))
    except:
        existing_creds = {'credentials': {}}

    if cloud in existing_creds['credentials'].keys():
        c = existing_creds['credentials'][cloud]
        c[app.current_controller] = __format_creds(
            credentials)
    else:
        # Handle the case where path exists but an entry for the cloud
        # has yet to be added.
        existing_creds['credentials'][cloud] = {
            app.current_controller: __format_creds(
                credentials)
        }

    with open(cred_path, 'w') as cred_f:
        cred_f.write(yaml.safe_dump(existing_creds,
                                    default_flow_style=False))


def is_lxd_ready():
    """ routine for making sure lxd is configured for localhost deployments
    """
    if utils.lxd_version() < parse_version('2.9'):
        return controllers.use('lxdsetup').render(
            "The current version of LXD found on this system is not "
            "compatible. Please run the following to get the latest "
            "supported LXD:\n\n"
            "  sudo apt-add-repository ppa:ubuntu-lxc/lxd-stable\n"
            "  sudo apt-get update\n"
            "  sudo apt-get install lxd lxd-client\n\n"
            "Or if you're using the snap version:\n\n"
            "  sudo snap refresh lxd --candidate\n\n"
            "Once complete please re-run conjure-up."
        )

    if not utils.check_user_in_group('lxd'):
        return controllers.use('lxdsetup').render(
            "{} is not part of the LXD group. You will need "
            "to exit conjure-up and do one of the following: "
            " 1: Run `newgrp lxd` and re-launch conjure-up\n"
            " 2: Log out completely, Log in and "
            "re-launch conjure-up".format(os.environ['USER']))

    try:
        setup_lxdbr0_network()
        setup_conjureup0_network()
    except Exception as e:
        return controllers.use('lxdsetup').render(
            "Unable to determine an existing LXD network bridge, "
            "please make sure you've run `sudo lxd init` to configure "
            "LXD.\n\n{}".format(e)
        )

    if utils.lxd_has_ipv6():
        return controllers.use('lxdsetup').render(
            "The LXD bridge has IPv6 enabled. Currently this is "
            "unsupported by conjure-up. Please disable IPv6 and "
            "re-launch conjure-up\n\n"
            "Visit http://conjure-up.io/docs/en/users/#_lxd for "
            "information on how to disable IPv6.")

    app.log.debug("Found an IPv4 address, "
                  "assuming LXD is configured.")


def setup_conjureup0_network():
    """ This attempts to setup LXD network bridge for conjureup if not available
    """
    out = utils.run_script('lxc network show conjureup0', stdout=DEVNULL)
    if out.returncode != 0:
        out = utils.run_script('lxc network create conjureup0 '
                               'ipv4.address=10.99.0.1/24 '
                               'ipv4.nat=true '
                               'ipv6.address=none '
                               'ipv6.nat=false')
        if out.returncode != 0:
            raise Exception(
                "Failed to create LXD conjureup0 network bridge: {}".format(
                    out.stderr.decode()))


def setup_lxdbr0_network():
    """ This attempts to setup LXD networking if not available
    """
    try:
        utils.run('lxc network show lxdbr0', shell=True, check=True,
                  stdout=DEVNULL)
    except CalledProcessError:
        out = utils.run_script('lxc network create lxdbr0 '
                               'ipv4.address=10.0.8.1/24 '
                               'ipv4.nat=true '
                               'ipv6.address=none '
                               'ipv6.nat=false')
        if out.returncode != 0:
            raise Exception(
                "Failed to create LXD network bridge: {}".format(
                    out.stderr.decode()))
    out = utils.run_script(
        "lxc network show lxdbr0 | grep -q 'ipv4\.address:\snone'")
    if out.returncode == 0:
        network_set_cmds = [
            'lxc network set lxdbr0 ipv4.address 10.0.8.1/24',
            'lxc network set lxdbr0 ipv4.nat true'
        ]
        for n in network_set_cmds:
            out = utils.run_script(n)
            if out.returncode != 0:
                raise Exception("Problem with {}: {}".format(
                    n, out.stderr.decode()))
