#
# auth.py - MAAS Authentication
#
# Copyright 2014 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from subprocess import check_output
import os
import logging

log = logging.getLogger(__name__)


class MaasAuth:

    """ MAAS Authorization class
    """

    def __init__(self, api_url=None, api_key=None):
        """ Initialize with optional OAuth credentials
        """
        self.api_url = api_url if api_url else 'http://localhost/MAAS/api/1.0'
        self.api_key = api_key
        self.consumer_secret = ''

    @property
    def is_logged_in(self):
        """ Checks if we are logged into the MAAS api

        :rtype: bool
        """
        return True if self.api_key else False

    @property
    def consumer_key(self):
        """ Maas consumer key

        :rtype: str
        """
        return self.api_key.split(':')[0] if self.api_key else None

    @property
    def token_key(self):
        """ Maas oauth token key

        :rtype: str
        """
        return self.api_key.split(':')[1] if self.api_key else None

    @property
    def token_secret(self):
        """ Maas oauth token secret

        :rtype: str
        """
        return self.api_key.split(':')[2] if self.api_key else None

    def get_api_key(self, username='root'):
        """ MAAS api key

        :param username: (optional) MAAS user to query for credentials
        :type username: str
        """
        if os.path.isfile('/usr/sbin/maas-region-admin'):
            out = check_output(['sudo', 'maas-region-admin', 'apikey',
                                '--username', username])
            self.api_key = out.decode('ascii').split()[-1].rstrip('\n')
        else:
            raise Exception(
                'Unable to find maas-region-admin to query api key.')
