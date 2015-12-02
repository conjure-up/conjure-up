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
import shlex
from subprocess import check_output, call


class Juju:
    @classmethod
    def bootstrap(cls):
        """ Performs juju bootstrap
        """
        check_output(['juju', 'bootstrap', '--debug'])

    @classmethod
    def available(cls):
        """ Checks if juju is available

        Returns:
        True/False if juju status was successful and a environment is found
        """
        return 0 == call(['juju', 'status'])

    @classmethod
    def deploy(cls, charm, charm_config):
        """ Juju deploy service

        Arguments:
        charm: Name of charm(service) to deploy
        charm_config: YAML formatted service config
        """

        check_output(['juju', 'deploy', '--config', charm_config, charm])

    @classmethod
    def debug_log(cls, include="*"):
        """ Juju debug-log

        Arguments:
        include: Filter to query log output
        """
        check_output(['juju', 'debug-log', shlex.quote(include)])
