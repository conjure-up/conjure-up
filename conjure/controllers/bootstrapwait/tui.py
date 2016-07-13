from conjure import utils
from conjure.app_config import app
from conjure import controllers


def finish():
    controllers.use('deploystatus').render()


def render(deploy_future=None):
    while app.bootstrap.running:
        utils.info("Waiting for bootstrap to finish")
    finish()
