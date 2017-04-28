import os
import os.path as path
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError

import yaml

from conjureup import juju, utils
from conjureup.app_config import app
from conjureup.telemetry import track_event

cred_path = path.join(utils.juju_path(), 'credentials.yaml')


def __format_creds(creds):
    """ Formats the credentials into strings from the widgets values
    """
    formatted = {}
    formatted['auth-type'] = creds.AUTH_TYPE
    for field in creds.fields():
        if not field.storable:
            continue
        formatted[field.key] = field.value

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

    if 'default-credential' in existing_creds['credentials'][cloud]:
        return existing_creds['credentials'][cloud]['default-credential']

    # XXX we should really prompt to select because this is non-deterministic
    for k, v in existing_creds['credentials'][cloud].items():
        if 'default-region' in k:
            app.current_region = v
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
    try:
        lxd_init()
        app.log.debug("LXD is configured.")
    except Exception as e:
        raise


def lxd_init():
    """ Runs initial lxd init
    """
    app.log.debug("Determining if embedded LXD is setup and ready.")
    snap_user_data = os.environ.get('SNAP_USER_DATA', None)
    if snap_user_data:
        lxd_setup_path = Path(snap_user_data) / 'lxd.setup'
        if not lxd_setup_path.exists():

            # Grab list of available physical networks to bind our bridge to
            iface = None
            try:
                ifaces = utils.get_physical_network_interfaces()
                # Grab a physical network device that has an ip address
                iface = [i for i in ifaces
                         if utils.get_physical_network_ipaddr(i)][0]
            except Exception:
                raise

            lxd_init_cmds = [
                "lxc version",
                "lxd init --auto",
                'lxc config set core.https_address [::]:12001',
                'lxc profile device add default {iface} '
                'nic nictype=bridged '
                'parent=conjureup1 name={iface}'.format(iface=iface)
            ]
            for cmd in lxd_init_cmds:
                app.log.debug("LXD Init: {}".format(cmd))
                out = utils.run_script(cmd)
                if out.returncode != 0:
                    raise Exception(
                        "Problem running: {}:{}".format(
                            cmd,
                            out.stderr.decode('utf8')))

            setup_bridge_network(iface)
            setup_unused_bridge_network()
            lxd_setup_path.touch()


def setup_unused_bridge_network():
    """ Sets up an unused bridge that can be used with deployments such as
    OpenStack on LXD using NovaLXD.
    """
    out = utils.run_script('lxc network show conjureup0',
                           stdout=DEVNULL,
                           stderr=DEVNULL)
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


def setup_bridge_network(iface):
    """ Sets up our main network bridge to be used with Localhost deployments
    """
    try:
        utils.run('lxc network show conjureup1', shell=True, check=True,
                  stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError:
        out = utils.run_script('lxc network create conjureup1 '
                               'ipv4.address=10.100.0.1/24 '
                               'ipv4.nat=true '
                               'ipv6.address=none '
                               'ipv6.nat=false')
        if out.returncode != 0:
            raise Exception(
                "Failed to create LXD network bridge: {}".format(
                    out.stderr.decode()))

        utils.run_script(
            'lxc network attach-profile conjureup1 '
            'default {iface} {iface}'.format(
                iface=iface))


async def do_bootstrap(creds, msg_cb, fail_msg_cb):
    if not app.is_jaas:
        await pre_bootstrap(msg_cb)
        app.log.info('Bootstrapping Juju controller.')
        msg_cb('Bootstrapping Juju controller.')
        track_event("Juju Bootstrap", "Started", "")
        cloud_with_region = app.current_cloud
        if app.current_region:
            cloud_with_region = '/'.join([app.current_cloud,
                                          app.current_region])
        success = await juju.bootstrap(app.current_controller,
                                       cloud_with_region,
                                       app.current_model,
                                       credential=creds)
        if not success:
            pathbase = os.path.join(
                app.config['spell-dir'],
                '{}-bootstrap').format(app.current_controller)
            with open(pathbase + ".err") as errf:
                err_log = "\n".join(errf.readlines())
            msg = "Error bootstrapping controller: {}".format(err_log)
            app.log.error(msg)
            fail_msg_cb(msg)
            cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]
            raise Exception('Unable to bootstrap (cloud type: {})'.format(
                cloud_type))
            return

        app.log.info('Bootstrap complete.')
        msg_cb('Bootstrap complete.')
        track_event("Juju Bootstrap", "Done", "")

        await juju.login()  # login to the newly created (default) model

        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = app.juju.client.info.provider_type
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model

        await utils.run_step('00_post-bootstrap',
                             'post-bootstrap',
                             msg_cb,
                             'Juju Post-Bootstrap')
    else:
        app.log.info('Adding new model in the background.')
        msg_cb('Adding new model in the background.')
        track_event("Juju Add JaaS Model", "Started", "")
        await juju.add_model(app.current_model,
                             app.current_controller,
                             app.current_cloud)
        track_event("Juju Add JaaS Model", "Done", "")
        app.log.info('Add model complete.')
        msg_cb('Add model complete.')


async def pre_bootstrap(msg_cb):
    """ runs pre bootstrap script if exists
    """

    # Set provider type for post-bootstrap
    app.env['JUJU_PROVIDERTYPE'] = juju.get_cloud_types_by_name()[
        app.current_cloud]
    app.env['JUJU_CONTROLLER'] = app.current_controller
    app.env['JUJU_MODEL'] = app.current_model
    app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

    await utils.run_step('00_pre-bootstrap',
                         'pre-bootstrap',
                         msg_cb)
