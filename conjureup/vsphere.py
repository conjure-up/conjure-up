""" Module for interacting with VSphere
"""

import ssl

from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim


class VSphereInvalidLogin(vim.fault.InvalidLogin):
    """ Login was invalid, could be user or password mismatch
    """
    pass


class VSphereClient:
    def __init__(self, username, password, host, port=443):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.si = None
        self.content = None

    def login(self):
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()

        self.si = SmartConnect(host=self.host,
                               user=self.username,
                               pwd=self.password,
                               port=self.port,
                               sslContext=context)
        self._retrieve_content()

    def disconnect(self):
        return Disconnect(self.si)

    def _retrieve_content(self):
        self.content = self.si.RetrieveContent()

    def _get_view_obj(self, vim_type):
        return self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [vim_type],
            True)

    def get_hosts(self):
        view_obj = self._get_view_obj(vim.HostSystem)
        return [host for host in view_obj.view]

    def get_datacenters(self):
        view_obj = self._get_view_obj(vim.Datacenter)
        return [dc for dc in view_obj.view]
