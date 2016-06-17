from operator import attrgetter
import os

from bundleplacer.bundle import Bundle
from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config

from conjure.app_config import app


def get_bundleinfo():
    bundle_filename = os.path.join(app.config['spell-dir'], 'bundle.yaml')
    bundle = Bundle(filename=bundle_filename)
    services = sorted(bundle.services,
                      key=attrgetter('service_name'))

    return bundle_filename, bundle, services


def get_metadata_controller(bundle, bundle_filename):
    bundleplacer_cfg = Config(
        'bundle-placer',
        {
            'bundle_filename': bundle_filename,
            'bundle_key': None,
        })

    return MetadataController(bundle, bundleplacer_cfg)
