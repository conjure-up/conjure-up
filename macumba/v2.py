from .api import Base

from functools import partial

# https://github.com/juju/juju/blob/master/api/facadeversions.go
_FACADE_VERSIONS = {
    "Action":                       2,
    "Agent":                        2,
    "AgentTools":                   1,
    "AllModelWatcher":              2,
    "AllWatcher":                   1,
    "Annotations":                  2,
    "Application":                  1,
    "ApplicationScaler":            1,
    "Backups":                      1,
    "Block":                        2,
    "CharmRevisionUpdater":         2,
    "Charms":                       2,
    "Cleaner":                      2,
    "Client":                       1,
    "Cloud":                        1,
    "Controller":                   3,
    "Deployer":                     1,
    "DiscoverSpaces":               2,
    "DiskManager":                  2,
    "EntityWatcher":                2,
    "FilesystemAttachmentsWatcher": 2,
    "Firewaller":                   3,
    "HighAvailability":             2,
    "HostKeyReporter":              1,
    "ImageManager":                 2,
    "ImageMetadata":                2,
    "InstancePoller":               3,
    "KeyManager":                   1,
    "KeyUpdater":                   1,
    "LeadershipService":            2,
    "LifeFlag":                     1,
    "LogForwarding":                1,
    "Logger":                       1,
    "MachineActions":               1,
    "MachineManager":               2,
    "Machiner":                     1,
    "MeterStatus":                  1,
    "MetricsAdder":                 2,
    "MetricsDebug":                 2,
    "MetricsManager":               1,
    "MigrationFlag":                1,
    "MigrationMaster":              1,
    "MigrationMinion":              1,
    "MigrationStatusWatcher":       1,
    "MigrationTarget":              1,
    "ModelManager":                 2,
    "NotifyWatcher":                1,
    "Payloads":                     1,
    "PayloadsHookContext":          1,
    "Pinger":                       1,
    "Provisioner":                  3,
    "ProxyUpdater":                 1,
    "Reboot":                       2,
    "RelationUnitsWatcher":         1,
    "Resources":                    1,
    "ResourcesHookContext":         1,
    "Resumer":                      2,
    "RetryStrategy":                1,
    "Singular":                     1,
    "Spaces":                       2,
    "SSHClient":                    1,
    "StatusHistory":                2,
    "Storage":                      2,
    "StorageProvisioner":           2,
    "StringsWatcher":               1,
    "Subnets":                      2,
    "Undertaker":                   1,
    "UnitAssigner":                 1,
    "Uniter":                       4,
    "Upgrader":                     1,
    "UserManager":                  1,
    "VolumeAttachmentsWatcher":     2
}


class JujuClient(Base):
    """ Exposes Juju 2.0 facades

    Example:
    jujuc = JujuClient(
        'wss://10.0.3.53:17070/model/e712da7b-6808-49ec-8c90-113b26d1650d/api',
        'f2cbbb1f163f2ed8725e973e5eeaf51a')
    jujuc.Client(request="FullStatus")
    """
    API_VERSION = 2
    CREDS_VERSION = 3

    def __init__(self, url, password, user='user-admin', macaroons=None):
        for name, version in _FACADE_VERSIONS.items():
            setattr(self, name, partial(self._request,
                                        name_type=name,
                                        version=version))
        super().__init__(url, password, user, macaroons)

    def _request(self, name_type, version, request, params=None):
        """ Performs a request

            Params:
            name_type: Facade type
            version: Facade version
            request: Name of Juju API call
            params: Query options to pass to request
        """
        if params is None:
            params = {}

        if not isinstance(params, dict):
            raise Exception("Must be a dictionary of query parameters.")

        return self.call({'Type': name_type,
                          'Version': version,
                          'Request': request,
                          'Params': params})

    def call(self, params, timeout=None):
        """ Get json data from juju api daemon.

        Params:
        params: Additional params to be passed into request
        """
        with self.connlock:
            req_id = self.conn.do_send(params)

        return self.receive(req_id, timeout)
