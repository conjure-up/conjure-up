from operator import attrgetter
import os

from bundleplacer.bundle import Bundle

from conjureup.app_config import app


def get_bundleinfo():
    bundle_filename = os.path.join(app.config['spell-dir'], 'bundle.yaml')
    bundle = Bundle(filename=bundle_filename)
    services = sorted(bundle.services,
                      key=attrgetter('service_name'))

    return bundle_filename, bundle, services
