from conjureup import utils

from . import common


class BootstrapController(common.BaseBootstrapController):
    msg_cb = utils.info


_controller_class = BootstrapController
