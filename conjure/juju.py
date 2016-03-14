""" Juju helpers
"""
from conjure.shell import shell
from conjure.utils import Host
import os
import yaml
import json
import q
from macumba.v2 import JujuClient
from macumba.errors import LoginError
from functools import wraps


def requires_login(f):
    def _decorator(*args, **kwargs):
        if not Juju.is_authenticated:
            Juju.login()
        return f(*args, **kwargs)
    return wraps(f)(_decorator)


class JujuNotFoundException(Exception):
    """ The available config is not found """


class JujuModelUserNotFound(Exception):
    """ Unable to find user associated with model """


class JujuControllerNotFound(Exception):
    """ Unable to find controller """


class JujuModelNotFound(Exception):
    """ Unable to find models """


class JujuCloudNotFound(Exception):
    """ Unable to determine cloud """


class Juju:
    is_authenticated = False
    client = None
    user_tag = None

    @classmethod
    def login(cls, force=False):
        """ Login to Juju API server
        """
        if cls.is_authenticated is True and not force:
            return

        current_controller = cls.current_controller()
        if not current_controller:
            raise LoginError("Unable to determine current controller")

        env = cls.controller(current_controller)
        account = cls.account(current_controller)
        uuid = cls.model(cls.current_model())['model-uuid']
        server = env['api-endpoints'][0]
        cls.user_tag = "user-{}".format(account['current'])
        current_user = account['current']
        password = account['users'][current_user]['password']
        url = os.path.join('wss://', server, 'model', uuid, 'api')
        cls.client = JujuClient(
            user=cls.user_tag,
            url=url,
            password=password)
        try:
            cls.client.login()
        except LoginError as e:
            raise e
        cls.is_authenticated = True

    @classmethod
    def bootstrap(cls, controller, cloud, upload_tools=True):
        """ Performs juju bootstrap

        Arguments:
        controller: name of your controller
        cloud: name of local or public cloud to deploy to
        upload_tools: True/False if you want to pass in --upload-tools
        """
        cmd = "juju bootstrap {} {}".format(controller, cloud)
        if upload_tools:
            cmd += " --upload-tools"
        return shell(cmd)

    @classmethod
    def available(cls):
        """ Checks if juju is available

        Returns:
        True/False if juju status was successful and a environment is found
        """
        return 0 == shell('juju status').code

    @classmethod
    def credential(cls, cloud, user):
        """ Get credentials for user

        Arguments:
        cloud: cloud applicable to user credentials
        user: user listed in the credentials
        """
        creds = cls.credentials()
        if cloud in creds.keys():
            if user in creds[cloud].keys():
                return creds[cloud][user]
        raise JujuModelUserNotFound(
            "Unable to locate credentials for: {}".format(user))

    @classmethod
    def credentials(cls, secrets=False):
        """ List credentials

        Arguments:
        secrets: True/False whether to show secrets (ie password)

        Returns:
        List of credentials
        """
        cmd = 'juju list-credentials --format yaml'
        if secrets:
            cmd += ' --show-secrets'
        sh = shell(cmd)
        if sh.code > 0:
            raise JujuNotFoundException(
                "Unable to list credentials: {}".format(sh.errors()))
        env = yaml.safe_load("\n".join(sh.output()))
        return env['credentials']

    @classmethod
    def clouds(cls):
        """ List available clouds

        Returns:
        Dictionary of all known clouds including newly created MAAS/Local
        """
        sh = shell('juju list-clouds --format yaml')
        if sh.code > 0:
            raise JujuNotFoundException(
                "Unable to list clouds: {}".format(sh.errors())
            )
        return yaml.safe_load("\n".join(sh.output()))

    @classmethod
    def cloud(cls, name):
        """ Return specific cloud information

        Arguments:
        name: name of cloud to query, ie. aws, lxd, local:provider
        Returns:
        Dictionary of cloud attributes
        """
        if name in cls.clouds().keys():
            return cls.clouds()[name]
        raise JujuCloudNotFound("Unable to locate cloud: {}".format(name))

    @classmethod
    def switch(cls, model):
        """ Switch to a Juju Model

        Arguments:
        model: Model to select

        Returns:
        False if failed to switch to Juju Model.
        """
        ret = 0 == shell('juju switch {}'.format(model)).code
        if ret:
            cls.login(True)
        return ret

    @classmethod
    def status(cls):
        """ Status of current model

        Returns:
        Dictionary of status
        """
        sh = shell('juju status --format yaml')
        if sh.code > 0:
            raise JujuNotFoundException(
                "Unable to get status output: {}".format(sh.errors()))
        return yaml.safe_load("\n".join(sh.output()))

    @classmethod
    def deploy_bundle(cls, bundle):
        """ Juju deploy bundle

        Arguments:
        bundle: Name of bundle to deploy, can be a path to local bundle file or
                charmstore path.
        """
        return shell('juju deploy {}'.format(bundle))

    @classmethod
    def current_controller(cls):
        """ Grabs the current default controller
        """
        env = os.path.join(Host.juju_path(), 'current-controller')
        if not os.path.isfile(env):
            return None
        with open(env) as fp:
            return fp.read().strip()

    @classmethod
    def controller(cls, controller):
        """ Return specific controller

        Arguments:
        controller: controller id
        """
        controllers = cls.controllers()
        if controllers and controller in controllers:
            return controllers[controller]
        return None

    @classmethod
    def controllers(cls):
        """ List available controllers

        Returns:
        List of known controllers
        """
        sh = shell('juju list-controllers --format json')
        if sh.code > 0:
            raise JujuNotFoundException(
                "Unable to list controllers: {}".format(sh.errors()))
        env = json.loads(sh.output()[0])
        return env['controllers']

    @classmethod
    def account(cls, controller):
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
        accounts = cls.accounts()
        if accounts and controller in accounts:
            account['users'] = accounts[controller].get('accounts', [])
            account['current'] = accounts[controller].get(
                'current-account', None)
        return account

    @classmethod
    def accounts(cls):
        """ List available accounts

        Returns:
        List of known accounts
        """
        env = os.path.join(Host.juju_path(), 'accounts.yaml')
        if not os.path.isfile(env):
            raise JujuNotFoundException(
                "Unable to find: {}".format(env))
        with open(env, 'r') as c:
            env = yaml.load(c)
            return env['controllers']
        raise JujuControllerNotFound("Unable to find accounts")

    @classmethod
    def model_by_owner(cls, user):
        """ List model associated with user

        Arguments:
        user: username to query

        Returns:
        Dictionary containing model information for user
        """
        models = cls.models()
        for m in models:
            if m['owner'] == user:
                return m
        raise JujuModelUserNotFound(
            "Unable to find user: {}".format(
                user
            ))

    @classmethod
    def model(cls, name):
        """ List information for model

        Arguments:
        name: model name

        Returns:
        Dictionary of model information
        """
        models = cls.models()['models']
        for m in models:
            if m['name'] == name:
                return m
        raise JujuControllerNotFound(
            "Unable to find model: {}".format(name))

    @classmethod
    def models(cls):
        """ List available models

        Returns:
        List of known models
        """
        sh = shell('juju list-models --format yaml')
        if sh.code > 0:
            raise JujuNotFoundException(
                "Unable to list models: {}".format(sh.errors()))
        return yaml.safe_load("\n".join(sh.output()))

    @classmethod
    def current_model(cls):
        return cls.models()['current-model']

    @classmethod
    def model_cache(cls):
        """ Reads the model cache in ~/.local/share/juju/models/cache.yaml

        This is currently necessary as there is no way to tell what provider
        types are associated to a particular controller.
        """
        cache_path = os.path.join(Host.juju_path(), 'models/cache.yaml')
        q(cache_path)
        return yaml.safe_load(open(cache_path))
