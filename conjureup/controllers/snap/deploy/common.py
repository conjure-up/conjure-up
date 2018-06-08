import asyncio
import os
from datetime import datetime

import websockets

from conjureup import events, juju, utils
from conjureup.app_config import app


async def do_deploy(msg_cb):
    await events.ModelConnected.wait()

    for step in app.steps:
        await step.before_deploy(msg_cb=msg_cb)
    events.PreDeployComplete.set()

    msg = 'Deploying Applications.'
    app.log.info(msg)
    msg_cb(msg)

    datetimestr = datetime.now().strftime("%Y%m%d.%H%m")
    fn = os.path.join(app.env['CONJURE_UP_CACHEDIR'],
                      '{}-deployed-{}.yaml'.format(
                          app.env['CONJURE_UP_SPELL'],
                          datetimestr))
    utils.spew(fn, app.current_bundle.to_yaml())
    for attempt in range(3):
        try:
            await app.juju.client.deploy(fn)
            break  # success
        except websockets.ConnectionClosed:
            if attempt == 2:
                raise
            await asyncio.sleep(1)

    events.DeploymentComplete.set()


async def wait_for_applications(msg_cb):
    await events.DeploymentComplete.wait()

    for step in app.steps:
        await step.before_wait(msg_cb=msg_cb)

    msg = 'Waiting for deployment to settle.'
    app.log.info(msg)
    msg_cb(msg)

    await juju.wait_for_deployment()

    events.ModelSettled.set()
    msg = 'Model settled.'
    app.log.info(msg)
    msg_cb(msg)
