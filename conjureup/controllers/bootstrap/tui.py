from conjureup import utils

from . import common


class BootstrapController(common.BootstrapController):
    msg_cb = utils.info


_controller_class = BootstrapController
