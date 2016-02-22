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
from macumba.v2 import JujuClient
from macumba.errors import LoginError
from functools import wraps


def requires_login(f):
    def _decorator(*args, **kwargs):
        if not Juju.is_authenticated:
            Juju.login()
        return f(*args, **kwargs)
    return wraps(f)(_decorator)


class Juju:
    is_authenticated = False
    client = None

    @classmethod
    def login(cls, model='lxd'):
        """ Login to Juju API server
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
        try:
            cls.client.login()
        except LoginError as e:
            raise e
        cls.is_authenticated = True

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
    def switch(cls, jujumodel):
        """ Switch to a Juju Model

        Arguments:
        jujumodel: Model to select

        Returns:
        False if failed to switch to Juju Model.
        """
        return 0 == shell('juju switch {}'.format(jujumodel)).code

    @classmethod
    def deploy_bundle(cls, bundle):
        """ Juju deploy bundle

        Arguments:
        bundle: Name of bundle to deploy, can be a path to local bundle file or
                charmstore path.
        """
        return shell('juju deploy {}'.format(bundle))

    @classmethod
    def env(cls):
        """ Returns a parsed models/cache.yaml to dictionary
        """
        env = os.path.join(Host.juju_path(), 'models/cache.yaml')
        if not os.path.isfile(env):
            raise Exception('No cached environment found.')
        with open(env) as env_fp:
            return yaml.load(env_fp)

    @classmethod
    def current_env(cls):
        """ Grabs the current default environment
        """
        env = os.path.join(Host.juju_path(), 'current-model')
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
