import os
from datetime import datetime
from subprocess import CalledProcessError

from conjureup import errors, events, utils
from conjureup.app_config import app


async def do_deploy(msg_cb):
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
    try:
        for _app in app.current_bundle.applications:
            cmd = ['sudo', 'snap', 'install',
                   _app.snap, '--channel', _app.channel]
            if hasattr(_app, 'confinement') and _app.confinement:
                cmd += ['--{}'.format(_app.confinement)]
            ret, out, err = await utils.arun(
                cmd,
                cb_stdout=msg_cb)
            if ret > 0:
                raise errors.DeploymentFailure(err)
    except CalledProcessError as e:
        app.log.error(
            "Could not snap install application: {}".format(e))
        raise

    events.DeploymentComplete.set()


async def wait_for_applications(msg_cb):
    await events.DeploymentComplete.wait()

    for step in app.steps:
        await step.before_wait(msg_cb=msg_cb)

    msg = 'Waiting for deployment to settle.'
    app.log.info(msg)
    msg_cb(msg)

    # await juju.wait_for_deployment()

    events.ModelSettled.set()
    msg = 'Model settled.'
    app.log.info(msg)
    msg_cb(msg)
