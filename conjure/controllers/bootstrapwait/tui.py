from conjure import utils
from conjure.app_config import app
from conjure import controllers


def finish(deploy_future=None):
    controllers.use('deploystatus').render(deploy_future)


def render(deploy_future=None):
    while app.bootstrap.running:
        utils.info(app.bootstrap.output)
    finish(deploy_future)
