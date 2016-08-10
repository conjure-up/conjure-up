from operator import attrgetter
import os

from bundleplacer.bundle import Bundle

from conjureup.app_config import app
from conjureup import charm


def get_bundleinfo():
    bundle_filename = os.path.join(app.config['spell-dir'], 'bundle.yaml')
    if not os.path.isfile(bundle_filename):
        bundle_filename = charm.get_bundle(
            app.config['metadata']['bundle-location'], True)
    bundle = Bundle(filename=bundle_filename)
    services = sorted(bundle.services,
                      key=attrgetter('service_name'))

    return bundle_filename, bundle, services
