""" Juju helpers
"""
import os
import sys
from concurrent import futures
from functools import partial, wraps
from subprocess import DEVNULL, PIPE, CalledProcessError, Popen, TimeoutExpired

import yaml

import macumba
from bundleplacer.charmstore_api import CharmStoreID
from conjureup import async
from conjureup.app_config import app
from conjureup.utils import juju_path, run
from macumba.v2 import JujuClient

JUJU_ASYNC_QUEUE = "juju-async-queue"

this = sys.modules[__name__]

# vars
this.IS_AUTHENTICATED = False
this.CLIENT = None
this.USER_TAG = None


# login decorator
def requires_login(f):
    def _decorator(*args, **kwargs):
        if not this.IS_AUTHENTICATED:
            login(force=True)
        return f(*args, **kwargs)
    return wraps(f)(_decorator)


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
    bootstrap_config = read_config("bootstrap-config")
    if 'controllers' not in bootstrap_config:
        raise Exception("Could not read Juju's bootstrap-config.yaml")
    cd = bootstrap_config['controllers'].get(controller_name, None)
    if cd is None:
        raise Exception("'{}' not found in Juju's "
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


def login(force=False):
    """ Login to Juju API server
    """
    if this.IS_AUTHENTICATED is True and not force:
        return

    if app.current_controller is None:
        raise Exception("Unable to determine current controller")

    if app.current_model is None:
        raise Exception("Tried to login with no current model set.")

    env = get_controller(app.current_controller)
    account = get_account(app.current_controller)
    uuid = get_model(app.current_controller, app.current_model)['model-uuid']
    server = env['api-endpoints'][0]
    this.USER_TAG = "user-{}".format(account['user'].split("@")[0])
    url = os.path.join('wss://', server, 'model', uuid, 'api')
    this.CLIENT = JujuClient(
        user=this.USER_TAG,
        url=url,
        password=account['password'])
    try:
        this.CLIENT.login()
    except macumba.errors.LoginError as e:
        raise e
    this.IS_AUTHENTICATED = True  # noqa


def bootstrap(controller, cloud, series="xenial", credential=None):
    """ Performs juju bootstrap

    If not LXD pass along the newly defined credentials

    Arguments:
    controller: name of your controller
    cloud: name of local or public cloud to deploy to
    series: define the bootstrap series defaults to xenial
    log: application logger
    credential: credentials key
    """
    cmd = "juju bootstrap {} {} " \
          "--config image-stream=daily ".format(
              cloud, controller)
    cmd += "--config enable-os-upgrade=false "
    cmd += "--default-model conjure-up "
    if app.argv.http_proxy:
        cmd += "--config http-proxy={} ".format(app.argv.http_proxy)
    if app.argv.https_proxy:
        cmd += "--config https-proxy={} ".format(app.argv.https_proxy)
    if app.argv.apt_http_proxy:
        cmd += "--config apt-http-proxy={} ".format(app.argv.apt_http_proxy)
    if app.argv.apt_https_proxy:
        cmd += "--config apt-https-proxy={} ".format(app.argv.apt_https_proxy)
    if app.argv.no_proxy:
        cmd += "--config no-proxy={} ".format(app.argv.no_proxy)
    if app.argv.bootstrap_timeout:
        cmd += "--config bootstrap-timeout={} ".format(
            app.argv.bootstrap_timeout)
    if app.argv.bootstrap_to:
        cmd += "--to {} ".format(app.argv.bootstrap_to)

    cmd += "--bootstrap-series={} ".format(series)
    if cloud != "localhost":
        cmd += "--credential {}".format(credential)
    app.log.debug("bootstrap cmd: {}".format(cmd))
    try:
        pathbase = os.path.join(app.config['spell-dir'],
                                '{}-bootstrap').format(app.current_controller)
        with open(pathbase + ".out", 'w') as outf:
            with open(pathbase + ".err", 'w') as errf:
                p = Popen(cmd, shell=True, stdout=outf,
                          stderr=errf)
                while p.poll() is None:
                    async.sleep_until(2)
                return p
    except CalledProcessError:
        raise Exception("Unable to bootstrap.")
    except async.ThreadCancelledException:
        p.terminate()
        try:
            p.wait(timeout=2)
        except TimeoutExpired:
            p.kill()
            p.wait()
        return p
    except Exception as e:
        raise e


def bootstrap_async(controller, cloud, credential=None, exc_cb=None):
    """ Performs a bootstrap asynchronously
    """
    return async.submit(partial(bootstrap,
                                controller=controller,
                                cloud=cloud,
                                credential=credential), exc_cb,
                        queue_name=JUJU_ASYNC_QUEUE)


def model_available():
    """ Checks if juju is available

    Returns:
    True/False if juju status was successful and a working model is found
    """
    try:
        run('juju status', shell=True,
            check=True, stderr=DEVNULL, stdout=DEVNULL)
    except CalledProcessError:
        return False
    return True


def autoload_credentials():
    """ Automatically checks known places for cloud credentials
    """
    try:
        run('juju autoload-credentials', shell=True, check=True)
    except CalledProcessError:
        return False
    return True


def get_credential(cloud, user):
    """ Get credentials for user

    Arguments:
    cloud: cloud applicable to user credentials
    user: user listed in the credentials
    """
    creds = get_credentials()
    if cloud in creds.keys():
        if user in creds[cloud].keys():
            return creds[cloud][user]
    raise Exception(
        "Unable to locate credentials for: {}".format(user))


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
    """Parses a constraint string into a dict"""
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
            constraint, constraint_value = c.split('=')
            new_constraints[constraint] = constraint_value
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


def add_machines(machines, msg_cb=None, exc_cb=None):
    """Add machines to model

    Arguments:

    machines: list of dictionaries of machine attributes.
    The key 'series' is required, and 'constraints' is the only other
    supported key

    """

    @requires_login
    def _add_machines_async():
        machine_params = [{"series": m['series'],
                           "constraints": constraints_to_dict(
                               m.get('constraints', "")),
                           "jobs": ["JobHostUnits"]}
                          for m in machines]
        app.log.debug("AddMachines: {}".format(machine_params))
        try:
            machine_response = this.CLIENT.Client(
                request="AddMachines", params={"params": machine_params})
            app.log.debug("AddMachines returned {}".format(machine_response))
        except Exception as e:
            if exc_cb:
                exc_cb(e)
            return

        if msg_cb:
            msg_cb("Added machines: {}".format(machine_response))
        return machine_response

    return async.submit(_add_machines_async,
                        exc_cb,
                        queue_name=JUJU_ASYNC_QUEUE)


def deploy_service(service, default_series, msg_cb=None, exc_cb=None):
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

    @requires_login
    def _deploy_async():

        if service.csid.rev == "":
            id_no_rev = service.csid.as_str_without_rev()
            mc = app.metadata_controller
            futures.wait([mc.metadata_future])
            info = mc.get_charm_info(id_no_rev, lambda _: None)
            service.csid = CharmStoreID(info["Id"])

        app.log.debug("Adding Charm {}".format(service.csid.as_str()))
        rv = this.CLIENT.Client(request="AddCharm",
                                params={"url": service.csid.as_str()})
        app.log.debug("AddCharm returned {}".format(rv))

        charm_id = service.csid.as_str()
        resources = app.metadata_controller.get_resources(charm_id)

        app.log.debug("Resources for charm id '{}': {}".format(charm_id,
                                                               resources))
        if resources:
            params = {"tag": "application-{}".format(service.csid.name),
                      "url": service.csid.as_str(),
                      "resources": resources}
            app.log.debug("AddPendingResources: {}".format(params))
            resource_ids = this.CLIENT.Resources(
                request="AddPendingResources",
                params=params)
            app.log.debug("AddPendingResources returned: {}".format(
                resource_ids))
            application_to_resource_map = {}
            for idx, resource in enumerate(resources):
                pid = resource_ids['pending-ids'][idx]
                application_to_resource_map[resource['Name']] = pid
            service.resources = application_to_resource_map

        deploy_args = service.as_deployargs()
        deploy_args['series'] = service.csid.series
        app_params = {"applications": [deploy_args]}

        app.log.debug("Deploying {}: {}".format(service, app_params))

        deploy_message = "Deploying {}... ".format(
            service.service_name)
        if msg_cb:
            msg_cb("{}".format(deploy_message))
        rv = this.CLIENT.Application(request="Deploy",
                                     params=app_params)
        app.log.debug("Deploy returned {}".format(rv))

        for result in rv.get('results', []):
            if 'error' in result:
                raise Exception("Error deploying: {}".format(
                    result['error'].get('message', 'error')))

        if msg_cb:
            msg_cb("{}: deployed, installing.".format(service.service_name))

        if service.expose:
            expose_params = {"application": service.service_name}
            app.log.debug("Expose: {}".format(expose_params))
            rv = this.CLIENT.Application(
                request="Expose",
                params=expose_params)
            app.log.debug("Expose returned: {}".format(rv))

    return async.submit(_deploy_async,
                        exc_cb,
                        queue_name=JUJU_ASYNC_QUEUE)


def set_relations(services, msg_cb=None, exc_cb=None):
    """ Juju set relations

    Arguments:
    services: list of services with relations to set
    msg_cb: message callback
    exc_cb: exception handler callback
    """
    relations = set()
    for service in services:
        for a, b in service.relations:
            if (a, b) not in relations and (b, a) not in relations:
                relations.add((a, b))

    @requires_login
    def do_add_all():
        if msg_cb:
            msg_cb("Setting application relations")

        for a, b in list(relations):
            params = {"Endpoints": [a, b]}
            try:
                app.log.debug("AddRelation: {}".format(params))
                rv = this.CLIENT.Application(request="AddRelation",
                                             params=params)
                app.log.debug("AddRelation returned: {}".format(rv))
            except Exception as e:
                if exc_cb:
                    exc_cb(e)
                return
        if msg_cb:
            msg_cb("Completed setting application relations")

    return async.submit(do_add_all,
                        exc_cb,
                        queue_name=JUJU_ASYNC_QUEUE)


def get_controller_info(name=None):
    """ Returns information on current controller

    Arguments:
    name: if set shows info controller, otherwise displays current.
    """
    cmd = 'juju show-controller --format yaml'
    if name is not None:
        cmd += ' {}'.format(name)
    sh = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise Exception(
            "Unable to determine controller: {}".format(
                sh.stderr.decode('utf8')))
    out = yaml.safe_load(sh.stdout.decode('utf8'))
    try:
        return next(iter(out.values()))
    except:
        return out


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


def add_model(name, controller):
    """ Adds a model to current controller

    Arguments:
    controller: controller to add model in
    """
    sh = run('juju add-model {} -c {}'.format(name, controller),
             shell=True, stdout=DEVNULL, stderr=PIPE)
    if sh.returncode > 0:
        raise Exception(
            "Unable to create model: {}".format(sh.stderr.decode('utf8')))


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
