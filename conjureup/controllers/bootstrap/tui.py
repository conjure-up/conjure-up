from functools import partial

from conjureup import utils

from . import common


class BootstrapController(common.BaseBootstrapController):
    msg_cb = partial(utils.info)


_controller_class = BootstrapController
