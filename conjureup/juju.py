""" Juju helpers
"""
import asyncio
import json
import logging
import os
from concurrent import futures
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError
from tempfile import NamedTemporaryFile

import yaml
from bundleplacer.charmstore_api import CharmStoreID
from juju.model import Model

from conjureup import consts, events, utils
from conjureup.app_config import app
from conjureup.utils import is_linux, juju_path, run, spew

JUJU_ASYNC_QUEUE = "juju-async-queue"

PENDING_DEPLOYS = 0


class ControllerNotFoundException(Exception):
    "An error when a controller can't be found in juju's config"


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
        raise ControllerNotFoundException(
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


async def login():
    """ Login to Juju API server
    """
    if app.juju.authenticated:
        return

    if app.provider.controller is None:
        raise Exception("Unable to determine current controller")

    if app.provider.model is None:
        raise Exception("Tried to login with no current model set.")

    app.juju.client = Model(app.loop)
    model_name = '{}:{}'.format(app.provider.controller,
                                app.provider.model)

    if not events.ModelAvailable.is_set():
        await events.ModelAvailable.wait()
    app.log.info('Connecting to model {}...'.format(model_name))
    await app.juju.client.connect_model(model_name)
    app.juju.authenticated = True
    events.ModelConnected.set()
    app.log.info('Connected')


async def bootstrap(controller, cloud, model='conjure-up', series="xenial",
                    credential=None):
    """ Performs juju bootstrap

    If not LXD pass along the newly defined credentials

    Arguments:
    controller: name of your controller
    cloud: name of local or public cloud to deploy to
    model: name of default model to create
    series: define the bootstrap series defaults to xenial
    credential: credentials key
    """
    if app.provider.region is not None:
        app.log.debug("Bootstrapping to set region: {}")
        cloud = "{}/{}".format(app.provider.cloud, app.provider.region)

    cmd = ["juju", "bootstrap", cloud, controller, "--default-model", model]

    def add_config(k, v):
        cmd.extend(["--config", "{}={}".format(k, v)])

    def add_model_defaults(k, v):
        cmd.extend(["--model-default", "{}={}".format(k, v)])

    if app.provider.model_defaults:
        for k, v in app.provider.model_defaults.items():
            add_model_defaults(k, v)

    add_config("image-stream", "daily"),
    add_config("enable-os-upgrade", "false"),
    if app.argv.http_proxy:
        add_config("http-proxy", app.argv.http_proxy)
    if app.argv.https_proxy:
        add_config("https-proxy", app.argv.https_proxy)
    if app.argv.apt_http_proxy:
        add_config("apt-http-proxy", app.argv.apt_http_proxy)
    if app.argv.apt_https_proxy:
        add_config("apt-https-proxy", app.argv.apt_https_proxy)
    if app.argv.no_proxy:
        add_config("no-proxy", app.argv.no_proxy)
    if app.argv.bootstrap_timeout:
        add_config("bootstrap-timeout", app.argv.bootstrap_timeout)
    if app.argv.bootstrap_to:
        cmd.extend(["--to", app.argv.bootstrap_to])

    cmd.extend(["--bootstrap-series", series])
    if credential is not None:
        cmd.extend(["--credential", credential])

    if app.argv.debug:
        cmd.append("--debug")
    app.log.debug("bootstrap cmd: {}".format(cmd))

    pathbase = os.path.join(app.config['spell-dir'],
                            '{}-bootstrap').format(app.provider.controller)
    with open(pathbase + ".out", 'w') as outf:
        with open(pathbase + ".err", 'w') as errf:
            proc = await asyncio.create_subprocess_exec(*cmd,
                                                        stdout=outf,
                                                        stderr=errf)
            app.log.debug('waiting for proc')
            await proc.wait()
            app.log.debug('proc done')
    if proc.returncode < 0:
        raise Exception('Bootstrap killed by user: {}'.format(
            proc.returncode))
    elif proc.returncode > 0:
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


async def model_available(name):
    """ Checks if juju is available

    Returns:
    True/False if juju status was successful and a working model is found
    """
    proc = await asyncio.create_subprocess_exec(
        'juju', 'status', '-m', ':'.join([app.provider.controller, name]),
        stderr=DEVNULL,
        stdout=DEVNULL)
    await proc.wait()
    return proc.returncode == 0


def autoload_credentials():
    """ Automatically checks known places for cloud credentials
    """
    try:
        run('juju autoload-credentials', shell=True, check=True)
    except CalledProcessError:
        return False
    return True


def get_credential(cloud, user=None):
    """ Get credentials for user

    Arguments:
    cloud: cloud applicable to user credentials
    user: user listed in the credentials
    """
    creds = get_credentials()
    if cloud not in creds.keys():
        return None

    if user and user in creds[cloud].keys():
        return creds[cloud][user]
    elif app.provider.controller in creds[cloud].keys():
        return creds[cloud][app.provider.controller]
    else:
        try:
            return next(iter(creds[cloud].values()))
        except StopIteration:
            app.log.debug("Unable to pull a credential from: {}".format(cloud))
            return None


def get_credentials(secrets=True):
    """ List credentials

    This will fallback to reading the credentials file directly

    Arguments:
    secrets: True/False whether to show secrets (ie password)

    Returns:
    List of credentials
    """
    cmd = 'juju list-credentials --format yaml'
    if secrets:
        cmd += ' --show-secrets'
    sh = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        try:
            env = read_config('credentials')
            return env['credentials']
        except:
            raise Exception(
                "Unable to list credentials: {}".format(
                    sh.stderr.decode('utf8')))
    env = yaml.safe_load(sh.stdout.decode('utf8'))
    return env['credentials']


def get_regions(cloud):
    """ List available regions for cloud

    Arguments:
    cloud: Cloud to list regions for

    Returns:
    Dictionary of all known regions for cloud
    """
    sh = run('juju list-regions {} --format yaml'.format(cloud),
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
    sh = run('juju list-clouds --format yaml',
             shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise Exception(
            "Unable to list clouds: {}".format(sh.stderr.decode('utf8'))
        )
    return yaml.safe_load(sh.stdout.decode('utf8'))


def get_compatible_clouds(cloud_types=None):
    """ List cloud types compatible with the current spell and controller.

    Arguments:
    clouds: optional initial list of clouds to filter
    Returns:
    List of cloud types
    """
    clouds = get_clouds()
    cloud_types = set(cloud_types or (c['type'] for c in clouds.values()))

    if 'lxd' in cloud_types:
        # normalize 'lxd' cloud type to localhost; 'lxd' can happen
        # depending on how the controller was bootstrapped
        cloud_types -= {'lxd'}
        cloud_types |= {'localhost'}

    if not is_linux():
        # LXD not available on macOS
        cloud_types -= {'localhost'}

    if app.provider and app.provider.controller:
        # if we already have a controller, we should query
        # it via the API for what clouds it supports; for now,
        # though, just assume it's JAAS and hard-code the options
        cloud_types &= consts.JAAS_CLOUDS

    whitelist = set(app.config['metadata'].get('cloud-whitelist', []))
    blacklist = set(app.config['metadata'].get('cloud-blacklist', []))
    if len(whitelist) > 0:
        return sorted(cloud_types & whitelist)

    elif len(blacklist) > 0:
        return sorted(cloud_types ^ blacklist)

    return sorted(cloud_types)


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

    # Since MAAS is a provider type and not identified as a cloud
    # we special case this so that selecting MAAS acts like any
    # other cloud selection.
    if 'maas' not in clouds:
        clouds['maas'] = 'maas'

    # vSphere is treated in the same vein as MAAS
    if 'vsphere' not in clouds:
        clouds['vsphere'] = 'vsphere'

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
        sh = run('juju add-cloud {} {}'.format(name, tempf.name),
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
    """Parses a constraint string into a dict. Does not do unit
    conversion. Expects root-disk, mem and cores to be int values, and
    root-disk and mem should be in megabytes."""
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
            elif constraint in ['root-disk', 'mem', 'cores']:
                value = int(value)
            else:
                raise Exception(
                    "Unsupported constraint: {}".format(constraint))
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
        return run('juju deploy {}'.format(bundle), shell=True,
                   stdout=DEVNULL, stderr=PIPE)
    except CalledProcessError as e:
        raise e


async def add_machines(applications, machines, msg_cb):
    """Add machines to model

    Arguments:

    app: name of app to which the machines belong
    machines: a mapping of virtual machine numbers to machine attributes.
    The key 'series' is required, and 'constraints' is the only other
    supported key

    """
    if not events.PreDeployComplete.is_set():
        # block until after pre-deploy
        await events.PreDeployComplete.wait()

    new_machines = {}
    tasks = []
    for vmid in sorted(machines.keys()):
        if events.MachineCreated.is_set(vmid):
            tasks.append(asyncio.sleep(0))  # no-op
        elif events.MachinePending.is_set(vmid):
            tasks.append(events.MachineCreated.wait(vmid))
        else:
            events.MachinePending.set(vmid)
            machine = machines[vmid]
            series = machine['series']
            constraints = constraints_to_dict(machine.get('constraints', ''))
            tasks.append(app.juju.client.add_machine(series=series,
                                                     constraints=constraints))
            new_machines[vmid] = None

    if new_machines:
        msg = 'Adding machine{}: {}'.format(
            's' if len(new_machines) > 1 else '',
            ', '.join(
                '{}: ({}, {})'.format(v,
                                      machines[v]['series'],
                                      machines[v].get('constraints', ''))
                for v in sorted(new_machines.keys())),
        )
        app.log.info(msg)
        msg_cb(msg)
    else:
        app.log.info('No new machines to add for {}'.format(
            ', '.join(a.service_name for a in applications)))

    results = await asyncio.gather(*tasks)
    for vmid, task_result in zip(sorted(machines.keys()), results):
        if vmid not in new_machines:
            # this is an events.MachinePending.wait() or no-op result
            continue
        events.MachinePending.clear(vmid)
        events.MachineCreated.set(vmid)
        new_machines[vmid] = task_result.id

    if new_machines:
        msg = "Added machine{}: {}".format(
            's' if len(new_machines) > 1 else '',
            ', '.join(sorted(new_machines.keys())),
        )
        app.log.info(msg)
        msg_cb(msg)

    for application in applications:
        app.log.info('Machines available for application {}'.format(
            application.service_name
        ))
        events.AppMachinesCreated.set(application.service_name)
    return new_machines


async def deploy_service(service, default_series, msg_cb):
    """Juju deploy service.

    If the service's charm ID doesn't have a revno, will query charm
    store to get latest revno for the charm.

    If the service's charm ID has a series, use that, otherwise use
    the provided default series.

    Arguments:
    service: Service to deploy
    msg_cb: message callback
    exc_cb: exception handler callback

    Returns a future that will be completed after the deploy has been
    submitted to juju

    """
    name = service.service_name
    if not events.AppMachinesCreated.is_set(name):
        # block until we have machines
        await events.AppMachinesCreated.wait(name)
        app.log.debug('Machines for {} are ready'.format(name))

    if service.csid.rev == "":
        id_no_rev = service.csid.as_str_without_rev()
        mc = app.metadata_controller
        futures.wait([mc.metadata_future])
        info = mc.get_charm_info(id_no_rev, lambda _: None)
        service.csid = CharmStoreID(info["Id"])

    deploy_args = {}
    deploy_args = dict(
        entity_url=service.csid.as_str(),
        application_name=service.service_name,
        num_units=service.num_units,
        constraints=service.constraints,
        to=service.placement_spec,
        config=service.options,
    )

    msg = 'Deploying {}...'.format(service.service_name)
    app.log.info(msg)
    msg_cb(msg)
    from pprint import pformat
    app.log.debug(pformat(deploy_args))

    app_inst = await app.juju.client.deploy(**deploy_args)

    if service.expose:
        msg = 'Exposing {}.'.format(service.service_name)
        app.log.info(msg)
        msg_cb(msg)
        await app_inst.expose()

    msg = '{}: deployed, installing.'.format(service.service_name)
    app.log.info(msg)
    msg_cb(msg)

    events.AppDeployed.set(service.service_name)


async def set_relations(service, msg_cb):
    """ Juju set relations

    Arguments:
    service: service with relations to set
    """
    relations = set()
    for a, b in service.relations:
        rel_pair = tuple(sorted((a, b)))
        if rel_pair in relations:
            continue
        a_app = a.split(':')[0]
        b_app = b.split(':')[0]
        await asyncio.gather(
            events.AppDeployed.wait(a_app),
            events.AppDeployed.wait(b_app),
        )
        relations.add(rel_pair)

    for rel_pair in relations:
        rel_name = '{} <-> {}'.format(*rel_pair)
        pending = events.PendingRelations.is_set(rel_name)
        added = events.RelationsAdded.is_set(rel_name)
        if pending or added:
            continue

        msg = "Setting relation {}".format(rel_name)
        app.log.info(msg)
        msg_cb(msg)
        events.PendingRelations.set(rel_name)
        await app.juju.client.add_relation(*rel_pair)
        events.PendingRelations.clear(rel_name)
        events.RelationsAdded.set(rel_name)

    events.RelationsAdded.set(service.service_name)


def get_controller_info(name=None):
    """ Returns information on current controller

    Arguments:
    name: if set shows info controller, otherwise displays current.
    """
    cmd = 'juju show-controller --format yaml'
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
    sh = run('juju list-controllers --format yaml',
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
        if m['name'] == name:
            return m
    raise LookupError(
        "Unable to find model: {}".format(name))


async def add_model(name, controller, cloud, credential=None):
    """ Adds a model to current controller

    Arguments:
    controller: controller to add model in
    cloud: cloud/region to add model in
    credential: optional credential name to use (required unless localhost)
    """
    if await model_available(name):
        events.ModelAvailable.set()
        await login()
        return

    cmd = ['juju', 'add-model', name, cloud, '--controller', controller]
    if credential:
        cmd.extend(['--credential', credential])
    proc = await asyncio.create_subprocess_exec(*cmd,
                                                stdout=DEVNULL, stderr=PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode > 0:
        raise Exception(
            "Unable to create model: {}".format(stderr.decode('utf8')))
    # the CLI has to connect to the model at least once to
    # populate the model macaroons; model_available does this
    # and verifies the model is working
    if not await model_available(name):
        raise Exception("Unable to connect model after creation")
    events.ModelAvailable.set()
    await login()


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
    sh = run('juju list-models --format yaml -c {}'.format(controller),
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
    sh = run('juju version', shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise Exception(
            "Unable to get Juju Version".format(sh.stderr.decode('utf8')))
    out = sh.stdout.decode('utf8')
    if isinstance(out, list):
        return out.pop()
    else:
        return out
