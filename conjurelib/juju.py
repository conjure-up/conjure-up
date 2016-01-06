# Copyright (c) 2015 Canonical Ltd.
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
from .utils import Host
from .shell import shell


class Juju:
    cmd_prefix = "sudo -E -H -u {}".format(Host.install_user())

    @classmethod
    def bootstrap(cls):
        """ Performs juju bootstrap
        """
        return shell('{} juju bootstrap --debug'.format(cls.cmd_prefix))

    @classmethod
    def available(cls):
        """ Checks if juju is available

        Returns:
        True/False if juju status was successful and a environment is found
        """
        return 0 == shell('{} juju status'.format(cls.cmd_prefix)).code

    @classmethod
    def deploy_charm(cls, charm, charm_config):
        """ Juju deploy service

        Arguments:
        charm: Name of charm(service) to deploy
        charm_config: YAML formatted service config
        """
        return shell('{} juju deploy --config {} {}'.format(cls.cmd_prefix,
                                                            charm_config,
                                                            charm))

    @classmethod
    def deploy_bundle(cls, bundle):
        """ Juju deploy bundle

        Arguments:
        charm: Name of bundle to deploy
        """
        bundle_str = "cs:bundle/{}".format(bundle)
        return shell('{} juju deploy {}'.format(cls.cmd_prefix,
                                                bundle_str))
