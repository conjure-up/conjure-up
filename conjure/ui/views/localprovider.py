from ubuntui.dialog import Dialog, opts_to_ui
from ubuntui.ev import EventLoop
from conjure.models.jujumodels.local import LocalJujuModel


class LocalJujuModelView(Dialog):

    input_items = opts_to_ui(LocalJujuModel.config)

    def __init__(self, common, cb):
        self.common = common
        title = "Local Configuration"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
