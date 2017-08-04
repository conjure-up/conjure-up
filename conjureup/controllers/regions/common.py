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
        if app.provider.cloud not in self._default_regions:
            app.provider.region = None
            if len(app.provider.regions) == 1:
                app.provider.region = list(app.provider.regions)[0]
            if not app.provider.region:
                creds = juju.get_credentials().get(app.provider.cloud, {})
                app.provider.region = creds.get('default-region', None)
            if not app.provider.region:
                try:
                    schema = load_schema(app.provider.cloud)
                    app.provider.region = schema.default_region
                except Exception:
                    # if we can't find a schema for this cloud,
                    # just assume no default
                    pass
            self._default_regions[app.provider.cloud] = app.provider.region
        return self._default_regions[app.provider.cloud]

    @property
    def regions(self):
        if app.provider.cloud not in self._regions:
            if app.provider.cloud_type in ['maas', 'localhost']:
                # No regions for these providers
                regions = []
            elif len(app.provider.regions) > 0:
                regions = app.provider.regions
            else:
                regions = sorted(juju.get_regions(app.provider.cloud).keys())
            self._regions[app.provider.cloud] = regions
        return self._regions[app.provider.cloud]

    def finish(self, region):
        app.provider.region = region
        if app.provider.cloud_type == 'localhost':
            controllers.use('lxdsetup').render()
        elif app.provider.cloud_type == 'vsphere':
            controllers.use('vspheresetup').render()
        else:
            controllers.use('controllerpicker').render()
