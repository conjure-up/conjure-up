# Copyright (c) 2015, 2016 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Juju helpers
"""
from conjure.shell import shell
from conjure.utils import Host
import os
import yaml
import json
from macumba.v2 import JujuClient
from macumba.errors import LoginError
from functools import wraps
import q


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
    def login(cls):
        """ Login to Juju API server
        """
        if cls.is_authenticated is True:
            return

        current_controller = cls.current_controller()
        if not current_controller:
            raise LoginError("Unable to determine current controller")

        env = cls.controller(current_controller)
        account = cls.account(current_controller)
        uuid = env['uuid']
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
    def clouds(cls):
        """ List available clouds

        Returns:
        Dictionary of all known clouds including newly created MAAS/Local
        """
        sh = shell('juju list-clouds --format json')
        q(json.loads(sh.output()[0]))
        return json.loads(sh.output()[0])

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
        return 0 == shell('juju switch {}'.format(model)).code

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
        controllers = os.path.join(Host.juju_path(), 'controllers.yaml')
        if not os.path.isfile(controllers):
            raise JujuNotFoundException(
                "Unable to find: {}".format(controllers))
        with open(controllers, 'r') as c:
            env = yaml.load(c)
            return env['controllers']
        return None

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
    def model_by_user(cls, controller, user):
        """ List model associated with user

        Arguments:
        controller: controller to search
        user: username to query

        Returns:
        Dictionary containing the current model and associated models

        eg: {'current': 'mycontroller',
             'models': [{'mycontroller': {
                             'uuid' : fdsa
                            }
                        }]}
        """
        model = cls.model(controller)
        if model and user in model:
            return model[user]
        raise JujuModelUserNotFound(
            "Unable to find user: {} in controller: {}".format(
                user, controller
            ))

    @classmethod
    def model(cls, controller):
        """ List model information for model

        Arguments:
        controller: controller id

        Returns:
        List of accounts associated with model
        """
        models = cls.models()
        if models and controller in models:
            return models[controller]['accounts']
        raise JujuControllerNotFound(
            "Unable to find model for controller: {}".format(controller))

    @classmethod
    def models(cls):
        """ List available models

        Returns:
        List of known models
        """
        env = os.path.join(Host.juju_path(), 'models.yaml')
        if not os.path.isfile(env):
            raise JujuNotFoundException(
                "Unable to find: {}".format(env))
        with open(env, 'r') as c:
            env = yaml.load(c)
            return env['controllers']
        raise JujuModelNotFound("Unable to list models")
