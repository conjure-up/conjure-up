from conjure import utils
from conjure import controllers


def finish():
    controllers.use('deploystatus').render()


def render():
    utils.info("Waiting for bootstrap to finish")
    finish()
