from conjureup.app_config import app

from . import common


_controller_class = common.BootstrapController(app.ui.set_footer)
