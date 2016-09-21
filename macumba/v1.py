from .api import Base, query_cs
from .errors import ServerError
from .jobs import Jobs

# https://github.com/juju/juju/blob/master/api/facadeversions.go
_FACADE_VERSIONS = {
    "Action":                       0,
    "Addresser":                    1,
    "Agent":                        1,
    "AllWatcher":                   0,
    "AllEnvWatcher":                1,
    "Annotations":                  1,
    "Backups":                      0,
    "Block":                        1,
    "Charms":                       1,
    "CharmRevisionUpdater":         0,
    "Client":                       0,
    "Cleaner":                      1,
    "Deployer":                     0,
    "DiskManager":                  1,
    "EntityWatcher":                1,
    "Environment":                  0,
    "EnvironmentManager":           1,
    "FilesystemAttachmentsWatcher": 1,
    "Firewaller":                   1,
    "HighAvailability":             1,
    "ImageManager":                 1,
    "ImageMetadata":                1,
    "InstancePoller":               1,
    "KeyManager":                   0,
    "KeyUpdater":                   0,
    "LeadershipService":            1,
    "Logger":                       0,
    "MachineManager":               1,
    "Machiner":                     0,
    "MetricsManager":               0,
    "Networker":                    0,
    "NotifyWatcher":                0,
    "Pinger":                       0,
    "Provisioner":                  1,
    "Reboot":                       1,
    "RelationUnitsWatcher":         0,
    "Resumer":                      1,
    "Rsyslog":                      0,
    "Service":                      1,
    "Storage":                      1,
    "Spaces":                       1,
    "Subnets":                      1,
    "StorageProvisioner":           1,
    "StringsWatcher":               0,
    "SystemManager":                1,
    "Upgrader":                     0,
    "Uniter":                       2,
    "UserManager":                  0,
    "VolumeAttachmentsWatcher":     1,
}


class JujuClient(Base):
    API_VERSION = 1
    CREDS_VERSION = 2
    FACADE_VERSIONS = _FACADE_VERSIONS

    def status(self):
        """ Returns status of juju environment """
        return self.call(dict(Type="Client",
                              Request="FullStatus"),
                         timeout=60)

    def get_watcher(self):
        """ Returns watcher """
        return self.call(dict(Type="Client",
                              Request="WatchAll"))

    def get_watched_tasks(self, watcher_id):
        """ Returns a list of all watches for Id """
        return self.call(dict(Type="AllWatcher",
                              Request="Next",
                              Id=watcher_id))

    def add_charm(self, charm_url):
        """ Adds charm """
        return self.call(dict(Type="Client",
                              Request="AddCharm",
                              Params=dict(URL=charm_url)))

    def get_charm(self, charm_url):
        """ Get charm """
        return self.call(dict(Type='Client',
                              Request='CharmInfo',
                              Params=dict(CharmURL=charm_url)))

    def add_machine(self, series="", constraints={},
                    machine_spec="", parent_id="", container_type=""):
        """Allocate a new machine from the iaas provider.
        """
        if machine_spec:
            err_msg = "Cant specify machine spec with container_type/parent_id"
            assert not (parent_id or container_type), err_msg
            parent_id, container_type = machine_spec.split(":", 1)

        params = dict(
            Series=series,
            ContainerType=container_type,
            ParentId=parent_id,
            Constraints=self._prepare_constraints(constraints),
            Jobs=[Jobs.HostUnits])
        return self.add_machines([params])

    def add_machines(self, machines):
        """ Add machines """
        return self.call(dict(Type="Client",
                              Request="AddMachines",
                              Params=dict(MachineParams=machines)))

    def destroy_machines(self, machine_ids, force=False):
        params = {"MachineNames": machine_ids}
        if force:
            params["Force"] = True
        return self.call(dict(Type="Client",
                              Request="DestroyMachines",
                              Params=params))

    def resolved(self, unit_name, retry=0):
        """ Resolved """
        return self.call(dict(Type="Client",
                              Request="Resolved",
                              Params=dict(UnitName=unit_name,
                                          Retry=retry)))

    def get_public_address(self, target):
        """ Gets public address of instance """
        return self.call(dict(Type="Client",
                              Request="PublicAddress",
                              Params=dict(Target=target)))

    def info(self):
        """ Returns Juju environment state """
        return self.call(dict(Type="Client",
                              Request="EnvironmentInfo"))

    def get_env_constraints(self):
        """ Get environment constraints """
        return self.call(dict(Type="Client",
                              Request="GetEnvironmentConstraints"))

    def set_env_constraints(self, constraints):
        """ Set environment constraints """
        return self.call(dict(Type="Client",
                              Request="SetEnvironmentConstraints",
                              Params=constraints))

    def get_env_config(self):
        """ Get environment config """
        return self.call(dict(Type="Client",
                              Request="EnvironmentGet"))

    def set_env_config(self, config):
        """ Sets environment config variables """
        return self.call(dict(Type="Client",
                              Request="EnvironmentSet",
                              Params=dict(Config=config)))

    def add_relation(self, endpoint_a, endpoint_b):
        """ Adds relation between units """
        try:
            rv = self.call(dict(Type="Client",
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
        return self.call(dict(Type="Client",
                              Request="DestroyRelation",
                              Params=dict(Endpoints=[endpoint_a,
                                                     endpoint_b])))

    def deploy(self, charm, service_name, num_units=1, config_yaml="",
               constraints=None, machine_spec=""):
        """ Deploy a charm to an instance

        :param str charm: Name of charm
        :param str service_name: name of service
        :param int num_units: number of units
        :param str config_yaml: charm configuration options
        :param dict constraints: deploy constraints
        :param str machine_spec: Type of machine to deploy to
        :returns: Deployed charm status
        """
        params = {'ServiceName': service_name}

        charm_info = query_cs(charm)
        params['CharmUrl'] = charm_info['Id']
        params['NumUnits'] = num_units
        params['ConfigYAML'] = config_yaml

        if constraints:
            params['Constraints'] = self._prepare_constraints(
                constraints)
        if machine_spec:
            params['ToMachineSpec'] = machine_spec
        return self.call(dict(Type="Client",
                              Request="ServiceDeploy",
                              Params=dict(params)))

    def set_annotations(self, entity, entity_type, annotation):
        """ Sets annotations.
        :param dict annotation: dict with string pairs.
        """
        return self.call(dict(Type="Client",
                              Request="SetAnnotations",
                              Params=dict(Tag="%s-%s" % (entity_type, entity),
                                          Pairs=annotation)))

    def get_annotations(self, entity, entity_type):
        """ Gets annotations """
        return self.call(dict(Type="Client",
                              Request="GetAnnotations",
                              Params=dict(Tag="%s-%s" % (entity_type,
                                                         entity))))

    def set_config(self, service_name, config_keys):
        """ Sets machine config """
        return self.call(dict(Type="Client",
                              Request="ServiceSet",
                              Params=dict(ServiceName=service_name,
                                          Options=config_keys)))

    def unset_config(self, service_name, config_keys):
        """ Unsets machine config """
        return self.call(dict(Type="Client",
                              Request="ServiceUnset",
                              Params=dict(ServiceName=service_name,
                                          Options=config_keys)))

    def set_charm(self, service_name, charm_url, force=0):
        return self.call(dict(Type="Client",
                              Request="ServiceSetCharm",
                              Params=dict(ServiceName=service_name,
                                          CharmUrl=charm_url,
                                          Force=force)))

    def get_service(self, service_name):
        """ Get charm, config, constraits for srevice"""
        return self.call(dict(Type="Client",
                              Request="ServiceGet",
                              Params=dict(ServiceName=service_name)))

    def get_config(self, service_name):
        """ Get service configuration """
        svc = self.get_service(service_name)
        return svc['Config']

    def get_constraints(self, service_name):
        """ Get service constraints """
        return self.call(dict(Type="Client",
                              Request="GetServiceConstraints",
                              Params=dict(ServiceName=service_name)))

    def set_constraints(self, service_name, constraints):
        """ Sets service level constraints """
        return self.call(dict(Type="Client",
                              Request="SetServiceConstraints",
                              Params=dict(ServiceName=service_name,
                                          Constraints=constraints)))

    def update_service(self, service_name, charm_url, force_charm_url=0,
                       min_units=1, settings={}, constraints={}):
        """ Update service """
        return self.call(dict(Type="Client",
                              Request="SetServiceConstraints",
                              Params=dict(ServiceName=service_name,
                                          CharmUrl=charm_url,
                                          MinUnits=min_units,
                                          SettingsStrings=settings,
                                          Constraints=constraints)))

    def destroy_service(self, service_name):
        """ Destroy a service """
        return self.call(dict(Type="Client",
                              Request="ServiceDestroy",
                              Params=dict(ServiceName=service_name)))

    def expose(self, service_name):
        """ Expose a service """
        return self.call(dict(Type="Client",
                              Request="ServiceExpose",
                              Params=dict(ServiceName=service_name)))

    def unexpose(self, service_name):
        """ Unexpose service """
        return self.call(dict(Type="Client",
                              Request="ServiceUnexpose",
                              Params=dict(ServiceName=service_name)))

    def valid_relation_name(self, service_name):
        """ All possible relation names for service """
        return self.call(dict(Type="Client",
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

        return self.call(dict(Type="Client",
                              Request="AddServiceUnits",
                              Params=dict(params)))

    def remove_unit(self, unit_names):
        """ Removes unit """
        return self.call(dict(Type="Client",
                              Request="DestroyServiceUnits",
                              Params=dict(UnitNames=unit_names)))
