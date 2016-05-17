""" Juju helpers
"""
from conjure import async
from conjure.utils import juju_path
from functools import wraps, partial
from macumba.errors import LoginError
from macumba.v2 import JujuClient
from subprocess import run, PIPE, DEVNULL, CalledProcessError
import json
import os
import sys
import yaml


this = sys.modules[__name__]

# vars
this.IS_AUTHENTICATED = False
this.CLIENT = None
this.USER_TAG = None


# login decorator
def requires_login(f):
    def _decorator(*args, **kwargs):
        if not this.IS_AUTHENTICATED:
            login()
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


def get_current_controller():
    """ Grabs the current default controller
    """
    env = os.path.join(juju_path(), 'current-controller')
    if not os.path.isfile(env):
        return None
    with open(env) as fp:
        return fp.read().strip()


def get_controller(id):
    """ Return specific controller

    Arguments:
    id: controller id
    """
    if get_controllers() and id in get_controllers():
        return get_controllers()[id]
    return None


def login(force=False):
    """ Login to Juju API server
    """
    if not available():
        raise Exception("Tried to login to a non bootstrapped environment.")

    if this.IS_AUTHENTICATED is True and not force:
        return

    if not get_current_controller():
        raise LoginError("Unable to determine current controller")

    env = get_controller(get_current_controller())
    account = get_account(get_current_controller())
    uuid = get_model(get_current_model())['model-uuid']
    server = env['api-endpoints'][0]
    this.USER_TAG = "user-{}".format(account['current'])
    current_user = account['current']
    password = account['users'][current_user]['password']
    url = os.path.join('wss://', server, 'model', uuid, 'api')
    this.CLIENT = JujuClient(
        user=this.USER_TAG,
        url=url,
        password=password)
    try:
        this.CLIENT.login()
    except LoginError as e:
        raise e
    this.IS_AUTHENTICATED = True  # noqa


def bootstrap(controller, cloud, series="xenial", log=None):
    """ Performs juju bootstrap

    If not LXD pass along the newly defined credentials

    Arguments:
    controller: name of your controller
    cloud: name of local or public cloud to deploy to
    series: define the bootstrap series defaults to xenial
    log: application logger
    """
    cmd = "juju bootstrap {} {} --upload-tools " \
          "--config image-stream=daily ".format(
              controller, cloud, series)
    cmd += "--bootstrap-series={} ".format(series)
    if cloud != "localhost":
        cmd += "--credential {}".format(controller)
    if log:
        log.debug("bootstrap cmd: {}".format(cmd))
    return run(cmd)


def bootstrap_async(controller, cloud,
                    series="xenial", log=None, exc_cb=None):
    """ Performs a bootstrap asynchronously
    """
    return async.submit(partial(bootstrap, controller,
                                cloud, series, log), exc_cb)


def available():
    """ Checks if juju is available

    Returns:
    True/False if juju status was successful and a environment is found
    """
    try:
        run('juju status', shell=True, check=True, stderr=DEVNULL)
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


def switch(model):
    """ Switch to a Juju Model

    Arguments:
    model: Model to select

    Returns:
    False if failed to switch to Juju Model.
    """
    ret = 0 == run('juju switch {}'.format(model), shell=True).returncode
    if ret:
        login(True)
    return ret


def deploy(bundle):
    """ Juju deploy bundle

    Arguments:
    bundle: Name of bundle to deploy, can be a path to local bundle file or
            charmstore path.
    """
    try:
        run('juju deploy {}'.format(bundle), shell=True, check=True)
    except CalledProcessError as e:
        raise e


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
    sh = run('juju list-controllers --format json',
             shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise LookupError(
            "Unable to list controllers: {}".format(sh.stder))
    env = json.loads(sh.stdout.decode('utf8')[0])
    return env['controllers']


def get_account(controller):
    """ List account information for controller

    Arguments:
    controller: controller id

    Returns:
    Dictionary containing list of accounts for controller and the
    current account in use.

    eg: {'users': [accounts], 'current': 'admin@local'}
    """
    account = {
        'users': None,
        'current': None
    }
    accounts = get_accounts()
    if accounts and controller in accounts:
        account['users'] = accounts[controller].get('accounts', [])
        account['current'] = accounts[controller].get(
            'current-account', None)
    return account


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


def model_by_owner(user):
    """ List model associated with user

    Arguments:
    user: username to query

    Returns:
    Dictionary containing model information for user
    """
    models = get_models()
    for m in models:
        if m['owner'] == user:
            return m
    raise LookupError(
        "Unable to find user: {}".format(
            user
        ))


def get_model(name):
    """ List information for model

    Arguments:
    name: model name

    Returns:
    Dictionary of model information
    """
    models = get_models()['models']
    for m in models:
        if m['name'] == name:
            return m
    raise LookupError(
        "Unable to find model: {}".format(name))


def get_models():
    """ List available models

    Returns:
    List of known models
    """
    sh = run('juju list-models --format yaml',
             shell=True, stdout=PIPE, stderr=PIPE)
    if sh.returncode > 0:
        raise LookupError(
            "Unable to list models: {}".format(sh.stderr.decode('utf8')))
    out = yaml.safe_load(sh.stdout.decode('utf8'))
    return out


def get_current_model():
    return get_models()['current-model']


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
