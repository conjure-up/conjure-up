import os
from datetime import datetime

from conjureup import utils
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


async def run_before_config(msg_cb, done_cb):
    for step in app.all_steps:
        if not step.has_before_config:
            continue
        await step.before_config(msg_cb)
    if app.has_bundle_modifications:
        utils.setup_metadata_controller()
    done_cb()
