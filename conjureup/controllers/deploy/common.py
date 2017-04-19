import os
from datetime import datetime

from conjureup import events, utils
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


async def pre_deploy(msg_cb):
    """ runs pre deploy script if exists
    """
    app.log.info('Waiting for model connection')
    await events.ModelConnected.wait()
    app.log.info('Got model connection')

    # Set provider type for post-bootstrap
    app.env['JUJU_PROVIDERTYPE'] = app.juju.client.info.provider_type
    app.env['JUJU_CONTROLLER'] = app.current_controller
    app.env['JUJU_MODEL'] = app.current_model
    app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

    await utils.run_step('00_pre-deploy',
                         'pre-deploy',
                         msg_cb)
    events.PreDeployComplete.set()
