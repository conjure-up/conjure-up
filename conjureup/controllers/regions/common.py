from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.models.provider import load_schema


class BaseRegionsController:
    def __init__(self):
        # can't just determine these during __init__ because the controller
        # instance is cached and the BACK button means we can get called
        # multiple times with different clouds selected
        self._regions = {}
        self._default_regions = {}

    @property
    def default_region(self):
        if app.current_cloud not in self._default_regions:
            default_region = None
            if len(self.regions) == 1:
                default_region = self.regions[0]
            if not default_region:
                creds = juju.get_credentials().get(app.current_cloud, {})
                default_region = creds.get('default-region', None)
            if not default_region:
                try:
                    schema = load_schema(app.current_cloud)
                    default_region = schema.default_region
                except Exception:
                    # if we can't find a schema for this cloud,
                    # just assume no default
                    pass
            self._default_regions[app.current_cloud] = default_region
        return self._default_regions[app.current_cloud]

    @property
    def regions(self):
        if app.current_cloud not in self._regions:
            if app.current_cloud_type in ['maas', 'localhost']:
                # No regions for these providers
                regions = []
            else:
                regions = sorted(juju.get_regions(app.current_cloud).keys())
            self._regions[app.current_cloud] = regions
        return self._regions[app.current_cloud]

    def finish(self, region):
        app.current_region = region
        if app.current_cloud_type == 'localhost':
            controllers.use('lxdsetup').render()
        elif app.current_cloud_type == 'vsphere':
            controllers.use('vspheresetup').render()
        else:
            controllers.use('controllerpicker').render()
