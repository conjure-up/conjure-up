import asyncio
import json
from pathlib import Path
from subprocess import CalledProcessError

from pkg_resources import parse_version

from conjureup import utils
from conjureup.app_config import app


class LXDClientError(Exception):
    pass


class LXDClientJSONError(Exception):
    pass


class LXDClient:
    """ Simple wrapper around lxc query or the older curl option for querying
    LXD API server
    """

    def __init__(self):
        self.minimum_support_version = parse_version('2.16')
        self.available = False
        self.retry_query_count = 0
        self._set_lxd_dir_env()

    def _set_lxd_dir_env(self):
        """ Sets and updates correct environment
        """
        if Path('/snap/bin/lxd').exists():
            self.lxd_socket_dir = Path('/var/snap/lxd/common/lxd')
            app.env['LXD_DIR'] = str(self.lxd_socket_dir)
        elif Path('/usr/bin/lxd').exists():
            self.lxd_socket_dir = Path('/var/lib/lxd')
            app.env['LXD_DIR'] = str(self.lxd_socket_dir)

    async def query(self, method="GET", segment=''):
        """ Query lxc api server

        Example: lxd v2.17: lxc query /1.0 | jq .
        """
        segment_prefix = Path('/1.0')
        try:
            cmd = ['lxc', 'query', '--wait', '-X', method.upper(),
                   str(segment_prefix / segment)]
            _, out, err = await utils.arun(cmd)
            return json.loads(out)
        except json.decoder.JSONDecodeError:
            err = "Unable to parse JSON output from LXD"
            app.log.error(err)
            raise LXDClientJSONError(err)
        except FileNotFoundError as e:
            app.log.error(e)
            raise LXDClientError(e)
        except CalledProcessError as e:
            app.log.error(e)
            raise LXDClientError(e)

    async def is_server_available(self):
        """ Waits and checks if LXD server becomes available

        We'll want to loop here and ignore most errors until have retries have
        been met
        """
        try:
            return await self.query()
        except (LXDClientJSONError, LXDClientError):
            if self.retry_query_count == 10:
                raise
            self._set_lxd_dir_env()
            self.retry_query_count += 1
            asyncio.sleep(2)

    async def is_server_compatible(self):
        """ Checks if LXD server version is compatible with conjure-up
        """
        try:
            out = await self.query()
        except LXDClientError:
            return False
        server_ver = out['environment']['server_version']
        return parse_version(server_ver) <= self.minimum_support_version
