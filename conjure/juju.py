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
from .shell import shell
import os
import yaml
from macumba.v2 import JujuClient
from .models.juju import JujuState


class Juju:
    is_authenticated = False
    client = None
    juju_data_dir = os.getenv('JUJU_DATA',
                              os.path.expanduser('~/.local/share/juju'))

    @classmethod
    def login(cls, model='lxd'):
        """ Login to Juju API server

        Params:
        model: Model to access
        """
        if cls.is_authenticated is True:
            return
        env = cls.env()
        uuid = env['server-user'][model]['server-uuid']
        server = env['server-data'][uuid]['api-endpoints'][0]
        password = env['server-data'][uuid]['identities']['admin']
        url = os.path.join('wss://', server, 'model', uuid, 'api')
        cls.client = JujuClient(
            url=url,
            password=password)
        cls.client.login()
        cls.is_authenticated = True

    @classmethod
    def list_models(cls, user='user-admin'):
        """ List current known juju models for user

        Params:
        user: user to list models for (default: user-admin)
        """
        models = Juju.client.ModelManager(request="ListModels",
                                          params={'Tag': user})
        return [x['Name'] for x in models['UserModels']]

    @classmethod
    def bootstrap(cls):
        """ Performs juju bootstrap
        """
        return shell('juju bootstrap --upload-tools')

    @classmethod
    def available(cls):
        """ Checks if juju is available

        Returns:
        True/False if juju status was successful and a environment is found
        """
        return 0 == shell('juju status').code

    @classmethod
    def status(cls):
        """ Returns JujuState()
        """
        if not cls.is_authenticated:
            cls.login()
        return JujuState(cls.client)

    @classmethod
    def deploy_bundle(cls, bundle):
        """ Juju deploy bundle

        Arguments:
        bundle: Name of bundle to deploy, can be a path to local bundle file or
                charmstore path.
        """
        return shell('juju deploy {}'.format(bundle))

    @classmethod
    def create_environment(cls):
        """ Creates a Juju environments.yaml file to bootstrap.
        """
        env_f = os.path.join(cls.juju_data_dir, 'environments.yaml')

        if not os.path.exists(env_f):
            shell('juju init')

    @classmethod
    def read_environment_yaml(cls):
        """ Reads a Juju environments.yaml file.
        """
        env_f = os.path.join(cls.juju_data_dir, 'environments.yaml')
        if not os.path.isfile(env_f):
            raise Exception('Unable to find environments.yaml')
        with open(env_f) as fp:
            return yaml.load(fp)

    @classmethod
    def env(cls):
        """ Returns a parsed environments.yaml to dictionary
        """
        env = os.path.join(cls.juju_data_dir, 'models/cache.yaml')
        if not os.path.isfile(env):
            raise Exception('No cached environment found.')
        with open(env) as env_fp:
            return yaml.load(env_fp)

    @classmethod
    def current_env(cls):
        """ Grabs the current default environment
        """
        env = os.path.join(cls.juju_data_dir, 'current-model')
        if not os.path.isfile(env):
            return None
        with open(env) as fp:
            return fp.read().strip()

    @classmethod
    def list_envs(cls):
        """ List known juju environments
        """
        env = cls.env()
        return list(env['server-user'].keys())
