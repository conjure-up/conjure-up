import os
from datetime import datetime

from conjureup.app_config import app
from conjureup.bundlewriter import BundleWriter


def write_bundle(assignments):
    bundle = app.metadata_controller.bundle
    bw = BundleWriter(assignments, bundle)
    datetimestr = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    fn = os.path.join(app.env['CONJURE_UP_CACHEDIR'],
                      '{}-deployed-{}.yaml'.format(app.env['CONJURE_UP_SPELL'],
                                                   datetimestr))
    bw.write_bundle(fn)
