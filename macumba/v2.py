# Copyright 2014-2016 Canonical, Ltd.
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

from .api import Base, query_cs
from .errors import ServerError

# https://github.com/juju/juju/blob/master/api/facadeversions.go
_FACADE_VERSIONS = {
    "Action":                       1,
    "Addresser":                    2,
    "Agent":                        2,
    "AgentTools":                   1,
    "AllWatcher":                   1,
    "AllModelWatcher":              2,
    "Annotations":                  2,
    "Backups":                      1,
    "Block":                        2,
    "Charms":                       2,
    "CharmRevisionUpdater":         1,
    "Client":                       1,
    "Cleaner":                      2,
    "Controller":                   2,
    "Deployer":                     1,
    "DiskManager":                  2,
    "EntityWatcher":                2,
    "FilesystemAttachmentsWatcher": 2,
    "Firewaller":                   2,
    "HighAvailability":             2,
    "ImageManager":                 2,
    "ImageMetadata":                2,
    "InstancePoller":               2,
    "KeyManager":                   1,
    "KeyUpdater":                   1,
    "LeadershipService":            2,
    "Logger":                       1,
    "MachineManager":               2,
    "Machiner":                     1,
    "MetricsManager":               1,
    "MeterStatus":                  1,
    "MetricsAdder":                 2,
    "ModelManager":                 2,
    "Networker":                    1,
    "NotifyWatcher":                1,
    "Pinger":                       1,
    "Provisioner":                  2,
    "ProxyUpdater":                 1,
    "Reboot":                       2,
    "RelationUnitsWatcher":         1,
    "Resumer":                      2,
    "Service":                      3,
    "Storage":                      2,
    "Spaces":                       2,
    "Subnets":                      2,
    "StatusHistory":                2,
    "StorageProvisioner":           2,
    "StringsWatcher":               1,
    "Upgrader":                     1,
    "UnitAssigner":                 1,
    "Uniter":                       3,
    "UserManager":                  1,
    "VolumeAttachmentsWatcher":     2,
    "Undertaker":                   1,
}


class JujuClient(Base):
    API_VERSION = 2
    FACADE_VERSIONS = _FACADE_VERSIONS

    def deploy(self, charm, service_name, num_units=1, config_yaml="",
               constraints=None, placement=""):
        """ Deploy a charm to an instance

        :param str charm: Name of charm
        :param str service_name: name of service
        :param int num_units: number of units
        :param str config_yaml: charm configuration options
        :param dict constraints: deploy constraints
        :param str placement: placement of charm to machine
        :returns: Deployed charm status
        """
        params = {'ServiceName': service_name}

        _url = query_cs(charm)
        params['CharmUrl'] = _url['charm']['url']
        params['NumUnits'] = num_units
        params['ConfigYAML'] = config_yaml

        if constraints:
            params['Constraints'] = self._prepare_constraints(
                constraints)
        if placement:
            params['Placement'] = placement
        return self.call(dict(Type="Service",
                              Request="ServiceDeploy",
                              Params=dict(params)))

    def set_config(self, service_name, config_keys):
        """ Sets machine config """
        return self.call(dict(Type="Service",
                              Request="ServiceSet",
                              Params=dict(ServiceName=service_name,
                                          Options=config_keys)))

    def unset_config(self, service_name, config_keys):
        """ Unsets machine config """
        return self.call(dict(Type="Service",
                              Request="ServiceUnset",
                              Params=dict(ServiceName=service_name,
                                          Options=config_keys)))

    def set_charm(self, service_name, charm_url, force=0):
        return self.call(dict(Type="Service",
                              Request="ServiceSetCharm",
                              Params=dict(ServiceName=service_name,
                                          CharmUrl=charm_url,
                                          Force=force)))

    def get_service(self, service_name):
        """ Get charm, config, constraits for srevice"""
        return self.call(dict(Type="Service",
                              Request="ServiceGet",
                              Params=dict(ServiceName=service_name)))

    def get_config(self, service_name):
        """ Get service configuration """
        svc = self.get_service(service_name)
        return svc['Config']

    def get_constraints(self, service_name):
        """ Get service constraints """
        return self.call(dict(Type="Service",
                              Request="GetServiceConstraints",
                              Params=dict(ServiceName=service_name)))

    def set_constraints(self, service_name, constraints):
        """ Sets service level constraints """
        return self.call(dict(Type="Service",
                              Request="SetServiceConstraints",
                              Params=dict(ServiceName=service_name,
                                          Constraints=constraints)))

    def update_service(self, service_name, charm_url, force_charm_url=0,
                       min_units=1, settings={}, constraints={}):
        """ Update service """
        return self.call(dict(Type="Service",
                              Request="SetServiceConstraints",
                              Params=dict(ServiceName=service_name,
                                          CharmUrl=charm_url,
                                          MinUnits=min_units,
                                          SettingsStrings=settings,
                                          Constraints=constraints)))

    def destroy_service(self, service_name):
        """ Destroy a service """
        return self.call(dict(Type="Service",
                              Request="ServiceDestroy",
                              Params=dict(ServiceName=service_name)))

    def expose(self, service_name):
        """ Expose a service """
        return self.call(dict(Type="Service",
                              Request="ServiceExpose",
                              Params=dict(ServiceName=service_name)))

    def unexpose(self, service_name):
        """ Unexpose service """
        return self.call(dict(Type="Service",
                              Request="ServiceUnexpose",
                              Params=dict(ServiceName=service_name)))

    def valid_relation_name(self, service_name):
        """ All possible relation names for service """
        return self.call(dict(Type="Service",
                              Request="ServiceCharmRelations",
                              Params=dict(ServiceName=service_name)))

    def add_unit(self, service_name, num_units=1, machine_spec=""):
        """ Add unit

        :param str service_name: Name of charm
        :param int num_units: Number of units
        :param str machine_spec: Type of machine to deploy to
        :returns dict: Units added
        """
        params = {}
        params['ServiceName'] = service_name
        params['NumUnits'] = num_units
        if machine_spec:
            params['ToMachineSpec'] = machine_spec

        return self.call(dict(Type="Service",
                              Request="AddServiceUnits",
                              Params=dict(params)))

    def remove_unit(self, unit_names):
        """ Removes unit """
        return self.call(dict(Type="Service",
                              Request="DestroyServiceUnits",
                              Params=dict(UnitNames=unit_names)))

    def add_relation(self, endpoint_a, endpoint_b):
        """ Adds relation between units """
        try:
            rv = self.call(dict(Type="Service",
                                Request="AddRelation",
                                Params=dict(Endpoints=[endpoint_a,
                                                       endpoint_b])))
        except ServerError as e:
            # do not treat pre-existing relations as exceptions:
            if 'relation already exists' in e.response['Error']:
                rv = e.response
            else:
                raise e

        return rv

    def remove_relation(self, endpoint_a, endpoint_b):
        """ Removes relation """
        return self.call(dict(Type="Service",
                              Request="DestroyRelaiton",
                              Params=dict(Endpoints=[endpoint_a,
                                                     endpoint_b])))
