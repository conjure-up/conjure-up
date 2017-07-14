from conjureup import events, utils
from conjureup.app_config import app
from conjureup.models.step import StepModel


async def wait_for_applications(msg_cb):
    await events.DeploymentComplete.wait()
    msg = 'Waiting for deployment to settle.'
    app.log.info(msg)
    msg_cb(msg)

    step = StepModel({},
                     filename='00_deploy-done',
                     name='Deployment Watcher')
    await utils.run_step(step, msg_cb)

    events.ModelSettled.set()
    msg = 'Model settled.'
    app.log.info(msg)
    msg_cb(msg)
