from conjureup.app_config import app

from . import common


class BootstrapController(common.BootstrapController):
    msg_cb = app.ui.set_footer


_controller_class = BootstrapController
