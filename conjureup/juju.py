""" Juju helpers
"""
import asyncio
import json
import logging
import os
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError
from tempfile import NamedTemporaryFile

import yaml
from juju.client.jujudata import FileJujuData
from juju.controller import Controller
from juju.model import Model
from melddict import MeldDict

from conjureup import consts, errors, events, utils
from conjureup.app_config import app
from conjureup.utils import is_linux, juju_path, run, spew


def _check_bin_candidates(candidates, bin_property):
    """ Checks a list of binary paths to verify they exist and are
    executable
    """
    # search candidate paths, in order, for the binary (ie juju, juju-wait)
    # we don't use $PATH because we have definite preferences which one we use
    # and we don't want to leave it up to the user
    if not hasattr(app.juju, bin_property):
        raise errors.AppConfigAttributeError(
            "Unknown juju property: {}".format(bin_property))
    for candidate in candidates:
        if os.access(candidate, os.X_OK):
            setattr(app.juju, bin_property, candidate)
            app.log.debug("{} candidate found".format(bin_property))
            break
    else:
        raise errors.JujuBinaryNotFound(
            "Unable to locate a candidate executable for {}.".format(
                candidates))


def set_bin_path():
    """ Sets the juju binary path
    """
    candidates = [
        os.environ['JUJU'],
        '/snap/bin/juju',
        '/snap/bin/conjure-up.juju',
        '/usr/bin/juju',
        '/usr/local/bin/juju',
    ]
    _check_bin_candidates(candidates, 'bin_path')
    # Update $PATH so that we make sure this candidate is used
    # first.
    app.env['PATH'] = "{}:{}".format(Path(app.juju.bin_path).parent,
                                     app.env['PATH'])


def set_wait_path():
    """ Sets juju-wait path
    """
    candidates = [
        os.environ['JUJU_WAIT'],
        '/snap/bin/juju-wait',
        '/snap/bin/conjure-up.juju-wait',
        '/usr/bin/juju-wait',
        '/usr/local/bin/juju-wait',
    ]

    _check_bin_candidates(candidates, 'wait_path')


def read_config(name):
    """ Reads a juju config file

    Arguments:
    name: filename without extension (ext defaults to yaml)

    Returns:
    dictionary of yaml object
    """
    abs_path = os.path.join(juju_path(), "{}.yaml".format(name))
    if not os.path.isfile(abs_path):
        raise Exception("Cannot load {}".format(abs_path))
    return yaml.safe_load(open(abs_path))


def get_bootstrap_config(controller_name):
    try:
        bootstrap_config = read_config("bootstrap-config")
    except Exception:
        # We may be trying to access the bootstrap-config to quickly
        # between the time of juju bootstrap occurs and this function
        # is accessed.
        app.log.exception("Could not load bootstrap-config, "
                          "setting an empty controllers dict.")
        bootstrap_config = dict(controllers={})
    if 'controllers' not in bootstrap_config:
        raise Exception("Could not read Juju's bootstrap-config.yaml")
    cd = bootstrap_config['controllers'].get(controller_name, None)
    if cd is None:
        raise errors.ControllerNotFoundException(
            "'{}' not found in Juju's "
            "bootstrap-config.yaml".format(controller_name))
    return cd


def get_current_controller():
    """ Grabs the current default controller
    """
    try:
        return get_controllers()['current-controller']
    except KeyError:
        return None


def get_controller(id):
    """ Return specific controller

    Arguments:
    id: controller id
    """
    if 'controllers' in get_controllers() \
       and id in get_controllers()['controllers']:
        return get_controllers()['controllers'][id]
    return None


def get_controller_in_cloud(cloud):
    """ Returns a controller that is bootstrapped on the named cloud

    Arguments:
    cloud: cloud to check for

    Returns:
    available controller or None if nothing available
    """
    controllers = get_controllers()['controllers'].items()
    for controller_name, controller in controllers:
        if cloud == controller['cloud']:
            return controller_name
    return None


async def model_available():
    """ Check whether selected model is already available.
    """
    if app.provider.controller is None:
        raise Exception("No controller selected")

    if app.provider.model is None:
        raise Exception("No model selected.")

    controller = Controller(app.loop)
    await controller.connect(app.provider.controller)
    try:
        models = await controller.list_models()
        return app.provider.model in models
    finally:
        await controller.disconnect()


async def connect_model():
    """ Connect to the selected model.
    """
    if app.provider.controller is None:
        raise Exception("No controller selected")

    if app.provider.model is None:
        raise Exception("No model selected.")

    app.juju.client = Model(app.loop)
    model_name = '{}:{}'.format(app.provider.controller,
                                app.provider.model)
    await app.juju.client.connect(model_name)
    events.ModelConnected.set()


async def create_model():
    """ Creates the selected model.
    """
    if app.provider.controller is None:
        raise Exception("No controller selected")

    if app.provider.model is None:
        raise Exception("No model selected.")

    controller = Controller(app.loop)
    await controller.connect(app.provider.controller)
    try:
        app.juju.client = await controller.add_model(
            model_name=app.provider.model,
            cloud_name=app.provider.cloud,
            region=app.provider.region,
            credential_name=app.provider.credential,
            config=app.conjurefile.get('model-config', None))
        events.ModelConnected.set()
    finally:
        await controller.disconnect()


async def bootstrap(controller, cloud, model='conjure-up', credential=None):
    """ Performs juju bootstrap

    If not LXD pass along the newly defined credentials

    Arguments:
    controller: name of your controller
    cloud: name of local or public cloud to deploy to
    model: name of default model to create
    credential: credentials key
    """
    if app.provider.region is not None:
        app.log.debug("Bootstrapping to set region: {}")
        cloud = "{}/{}".format(app.provider.cloud, app.provider.region)

    cmd = [app.juju.bin_path, "bootstrap",
           cloud, controller, "--default-model", model]

    def add_config(k, v):
        cmd.extend(["--config", "{}={}".format(k, v)])

    app.provider.model_defaults = MeldDict(app.provider.model_defaults or {})
    app.provider.model_defaults.add(app.conjurefile.get('model-config', {}))
    if app.provider.model_defaults:
        for k, v in app.provider.model_defaults.items():
            if v is not None:
                add_config(k, v)

    add_config("image-stream", "daily")
    if app.conjurefile['http-proxy']:
        add_config("http-proxy", app.conjurefile['http-proxy'])
    if app.conjurefile['https-proxy']:
        add_config("https-proxy", app.conjurefile['https-proxy'])
    if app.conjurefile['apt-http-proxy']:
        add_config("apt-http-proxy", app.conjurefile['apt-http-proxy'])
    if app.conjurefile['apt-https-proxy']:
        add_config("apt-https-proxy", app.conjurefile['apt-https-proxy'])
    if app.conjurefile['no-proxy']:
        add_config("no-proxy", app.conjurefile['no-proxy'])
    if app.conjurefile['bootstrap-timeout']:
        add_config("bootstrap-timeout", app.conjurefile['bootstrap-timeout'])
    if app.conjurefile['bootstrap-to']:
        cmd.extend(["--to", app.conjurefile['bootstrap-to']])
    if app.conjurefile['bootstrap-series']:
        cmd.extend(["--bootstrap-series", app.conjurefile['bootstrap-series']])

    if credential is not None:
        cmd.extend(["--credential", credential])

    if app.conjurefile['debug']:
        cmd.append("--debug")
    app.log.debug("bootstrap cmd: {}".format(cmd))

    log_file = '{}-bootstrap'.format(app.provider.controller)
    path_base = str(Path(app.config['spell-dir']) / log_file)
    out_path = path_base + '.out'
    err_path = path_base + '.err'
    rc, _, _ = await utils.arun(cmd, stdout=out_path, stderr=err_path)
    if rc < 0:
        raise errors.BootstrapInterrupt('Bootstrap killed by user')
    elif rc > 0:
        return False
    events.ModelAvailable.set()
    return True


def has_jaas_auth():
    jaas_cookies = Path('~/.local/share/juju/cookies/jaas.json').expanduser()
    if jaas_cookies.exists():
        jaas_cookies = json.loads(jaas_cookies.read_text())
        for cookie in jaas_cookies or []:
            if cookie['Domain'] == consts.JAAS_DOMAIN:
                return bool(cookie['Value'])
    return False


async def register_controller(name, endpoint, email, password, twofa,
                              timeout=30, fail_cb=None, timeout_cb=None):
    app.log.info('Registering controller {}'.format(name))
    cmd = ['juju', 'login', '-B', endpoint, '-c', name]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
    )
    try:
        stdin = b''.join(b'%s\n' % bytes(f, 'utf8')
                         for f in [email, password, twofa])
        stdout, stderr = await asyncio.wait_for(proc.communicate(stdin),
                                                timeout)
        stdout = stdout.decode('utf8')
        stderr = stderr.decode('utf8')

        prefix = 'Enter a name for this controller: '
        if stderr.startswith(prefix):
            # Juju has started putting this one prompt out on stderr
            # instead of stdout for some reason, so we work around it.
            stderr = stderr[len(prefix):]
    except asyncio.TimeoutError:
        proc.kill()
        app.log.warning('Registration timed out')
        if timeout_cb:
            timeout_cb()
        elif fail_cb:
            fail_cb('Timed out')
        return False
    if proc.returncode != 0:
        app.log.warning('Registration failed: {}'.format(stderr))
        if fail_cb:
            fail_cb(stderr)
            return False
        else:
            raise CalledProcessError(cmd, stderr)
    app.log.info('Registration complete')
    return True


def autoload_credentials():
    """ Automatically checks known places for cloud credentials
    """
    try:
        run('{} autoload-credentials'.format(
            app.juju.bin_path), shell=True, check=True)
    except CalledProcessError:
        return False
    return True


def get_credential(cloud, cred_name=None):
    """ Get credential

    Arguments:
    cloud: cloud applicable to user credentials
    cred_name: name of credential to get, or default
    """
    creds = get_credentials()
    if cloud not in creds.keys():
        return None

    cred = creds[cloud]

    default_credential = cred.pop('default-credential', None)
    cred.pop('default-region', None)

    if cred_name is not None and cred_name in cred.keys():
        return cred[cred_name]
    elif default_credential is not None and default_credential in cred.keys():
        return cred[default_credential]
    elif len(cred) == 1:
        return list(cred.values())[0]
    else:
        return None


def get_credentials():
    """ Get all locally cached credentials from Juju.

    Returns:
    Dict of credentials by cloud.
    """
    try:
        return FileJujuData().credentials()
    except FileNotFoundError:
        return {}


def get_regions(cloud):
    """ List available regions for cloud

    Arguments:
    cloud: Cloud to list regions for

    Returns:
    Dictionary of all known regions for cloud
    """
    sh = run('{} list-regions {} --format yaml'.format(app.juju.bin_path,
                                                       cloud),
             shell=True, stdout=PIPE, stderr=PIPE)
    stdout = sh.stdout.decode('utf8')
    stderr = sh.stderr.decode('utf8')
    if sh.returncode > 0:
        raise Exception("Unable to list regions: {}".format(stderr))
    if 'no regions' in stdout:
        return {}
    result = yaml.safe_load(stdout)
    if not isinstance(result, dict):
        msg = 'Unexpected response from regions: {}'.format(result)
        app.log.error(msg)
        utils.sentry_report(msg, level=logging.ERROR)
        result = {}
    return result


def get_clouds():
    """ List available clouds

    Returns:
    Dictionary of all known clouds including newly created MAAS/Local
    """
    sh = run('{} list-clouds --local --format yaml'.format(app.juju.bin_path),
             shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise Exception(
            "Unable to list clouds: {}".format(sh.stderr.decode('utf8'))
        )
    return yaml.safe_load(sh.stdout.decode('utf8')) or {}


def get_compatible_clouds(cloud_types=None):
    """ List cloud types compatible with the current spell and controller.

    Arguments:
    clouds: optional initial list of clouds to filter
    Returns:
    List of cloud types
    """
    if cloud_types is None:
        clouds = get_clouds()
        cloud_types = set(c['type'] for c in clouds.values())
        # custom providers don't show up in list-clouds but are valid types
        cloud_types |= set(consts.CUSTOM_PROVIDERS)
    else:
        cloud_types = set(cloud_types)

    _normalize_cloud_types(cloud_types)

    if not is_linux():
        # LXD not available on macOS
        cloud_types -= {'localhost'}

    if app.provider and app.provider.controller:
        # if we already have a controller, we should query
        # it via the API for what clouds it supports; for now,
        # though, just assume it's JAAS and hard-code the options
        cloud_types &= consts.JAAS_CLOUDS

    whitelist = set(app.metadata.cloud_whitelist)
    blacklist = set(app.metadata.cloud_blacklist)

    addons_dir = Path(app.config['spell-dir']) / 'addons'
    for addon in app.selected_addons:
        addon_file = addons_dir / addon / 'metadata.yaml'
        addon_meta = yaml.safe_load(addon_file.read_text())
        whitelist.update(addon_meta.get('cloud-whitelist', []))
        blacklist.update(addon_meta.get('cloud-blacklist', []))

    _normalize_cloud_types(whitelist)
    _normalize_cloud_types(blacklist)

    if len(whitelist) > 0:
        return sorted(cloud_types & whitelist)

    elif len(blacklist) > 0:
        return sorted(cloud_types ^ blacklist)

    return sorted(cloud_types)


def _normalize_cloud_types(cloud_types):
    if 'lxd' in cloud_types:
        # normalize 'lxd' cloud type to localhost; 'lxd' can happen
        # depending on how the controller was bootstrapped
        cloud_types -= {'lxd'}
        cloud_types |= {'localhost'}

    if 'local' in cloud_types:
        cloud_types -= {'local'}
        cloud_types |= {'localhost'}

    if 'aws' in cloud_types:
        cloud_types -= {'aws'}
        cloud_types |= {'ec2'}

    if 'google' in cloud_types:
        cloud_types -= {'google'}
        cloud_types |= {'gce'}


def get_cloud_types_by_name():
    """ Return a mapping of cloud names to their type.

    This accounts for some normalizations that get_clouds() doesn't.
    """
    clouds = {n: c['type'] for n, c in get_clouds().items()}

    # normalize 'lxd' cloud type to localhost; 'lxd' can happen
    # depending on how the controller was bootstrapped
    for name, cloud_type in clouds.items():
        if cloud_type == 'lxd':
            clouds[name] = 'localhost'

    for provider in consts.CUSTOM_PROVIDERS:
        if provider not in clouds:
            clouds[provider] = provider

    return clouds


def add_cloud(name, config):
    """ Adds a cloud

    Arguments:
    name: name of cloud to add
    config: cloud configuration
    """
    _config = {
        'clouds': {
            name: config
        }
    }
    app.log.debug(_config)
    with NamedTemporaryFile(mode='w', encoding='utf-8',
                            delete=False) as tempf:
        output = yaml.safe_dump(_config, default_flow_style=False)
        spew(tempf.name, output)
        sh = run('{} add-cloud {} {}'.format(app.juju.bin_path,
                                             name, tempf.name),
                 shell=True, stdout=PIPE, stderr=PIPE)
        if sh.returncode > 0:
            raise Exception(
                "Unable to add cloud: {}".format(sh.stderr.decode('utf8')))


def get_cloud(name):
    """ Return specific cloud information

    Arguments:
    name: name of cloud to query, ie. aws, lxd, local:provider
    Returns:
    Dictionary of cloud attributes
    """
    if name in get_clouds().keys():
        return get_clouds()[name]
    raise LookupError("Unable to locate cloud: {}".format(name))


def constraints_to_dict(constraints):
    """
    Parses a constraint string into a dict. If tags and spaces are found they
    will be converted into a list. All other constraints are passed directly to
    juju for processing during deployment.
    """
    new_constraints = {}
    if not isinstance(constraints, str):
        app.log.debug(
            "Invalid constraints: {}, skipping".format(
                constraints))
        return new_constraints

    list_constraints = [c for c in constraints.split(' ')
                        if c != ""]
    for c in list_constraints:
        try:
            constraint, value = c.split('=')
            if constraint in ['tags', 'spaces']:
                value = value.split(',')
            else:
                pass
            new_constraints[constraint] = value
        except ValueError as e:
            app.log.debug("Skipping constraint: {} ({})".format(c, e))
    return new_constraints


def constraints_from_dict(cdict):
    return " ".join(["{}={}".format(k, v) for k, v in cdict.items()])


def deploy(bundle):
    """ Juju deploy bundle

    Arguments:
    bundle: Name of bundle to deploy, can be a path to local bundle file or
            charmstore path.
    """
    try:
        return run('{} deploy {}'.format(app.juju.bin_path,
                                         bundle), shell=True,
                   stdout=DEVNULL, stderr=PIPE)
    except CalledProcessError as e:
        raise e


def get_controller_info(name=None):
    """ Returns information on current controller

    Arguments:
    name: if set shows info controller, otherwise displays current.
    """
    cmd = '{} show-controller --format yaml'.format(
        app.juju.bin_path)
    if name is not None:
        cmd += ' {}'.format(name)
    sh = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    sh_out = sh.stdout.decode('utf8')
    sh_err = sh.stderr.decode('utf8')
    try:
        data = yaml.safe_load(sh_out)
    except yaml.parser.ParserError:
        data = None
    if sh.returncode != 0 or not data:
        raise Exception("Unable to get info for "
                        "controller {}: {}".format(name, sh_err))
    return next(iter(data.values()))


def get_controllers():
    """ List available controllers

    Returns:
    List of known controllers
    """
    sh = run('{} list-controllers --format yaml'.format(
        app.juju.bin_path),
        shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise LookupError(
            "Unable to list controllers: {}".format(sh.stderr.decode('utf8')))
    env = yaml.safe_load(sh.stdout.decode('utf8'))
    return env


def get_account(controller):
    """ List account information for controller

    Arguments:
    controller: controller id

    Returns:
    Dictionary containing list of accounts for controller and the
    current account in use.

    """
    return get_accounts().get(controller, {})


def get_accounts():
    """ List available accounts

    Returns:
    List of known accounts
    """
    env = os.path.join(juju_path(), 'accounts.yaml')
    if not os.path.isfile(env):
        raise Exception(
            "Unable to find: {}".format(env))
    with open(env, 'r') as c:
        env = yaml.load(c)
        return env['controllers']
    raise Exception("Unable to find accounts")


def get_model(controller, name):
    """ List information for model

    Arguments:
    name: model name
    controller: name of controller to work in

    Returns:
    Dictionary of model information
    """
    models = get_models(controller)['models']
    for m in models:
        if m['short-name'] == name:
            return m
    raise LookupError(
        "Unable to find model: {}".format(name))


async def destroy_model(controller, model):
    """ Destroys a model within a controller

    Arguments:
    controller: name of controller
    model: name of model to destroy
    """
    proc = await asyncio.create_subprocess_exec(
        'juju', 'destroy-model', '-y', ':'.join([controller, model]),
        stdout=DEVNULL, stderr=PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode > 0:
        raise Exception(
            "Unable to destroy model: {}".format(stderr.decode('utf8')))
    events.ModelAvailable.clear()


def get_models(controller):
    """ List available models

    Arguments:
    controller: existing controller to get models for

    Returns:
    List of known models
    """
    sh = run('{} list-models --format yaml -c {}'.format(app.juju.bin_path,
                                                         controller),
             shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise LookupError(
            "Unable to list models: {}".format(sh.stderr.decode('utf8')))
    out = yaml.safe_load(sh.stdout.decode('utf8'))
    return out


def get_current_model():
    try:
        return get_models()['current-model']
    except:
        return None


def version():
    """ Returns version of Juju
    """
    sh = run('{} version'.format(
        app.juju.bin_path),
        shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise Exception(
            "Unable to get Juju Version: {}".format(sh.stderr.decode('utf8')))
    out = sh.stdout.decode('utf8')
    if isinstance(out, list):
        return out.pop()
    else:
        return out


async def wait_for_deployment(retries=3):
    """ Waits for all deployed applications to settle
    """
    if 'CONJURE_UP_MODE' in app.env and app.env['CONJURE_UP_MODE'] == "test":
        retries = 0

    cmd = [app.juju.wait_path, "-r{}".format(retries),
           "-vwm", "{}:{}".format(app.provider.controller,
                                  app.provider.model)]

    out_path = str(Path(app.config['spell-dir']) / 'deploy-wait.out')
    err_path = str(Path(app.config['spell-dir']) / 'deploy-wait.err')

    ret, _, err_log = await utils.arun(cmd, stdout=out_path, stderr=err_path)
    if ret != 0:
        err_log_tail = err_log.splitlines()[-10:]
        app.log.error('\n'.join(err_log_tail))
        raise errors.DeploymentFailure(
            "Some applications failed to start successfully.")
