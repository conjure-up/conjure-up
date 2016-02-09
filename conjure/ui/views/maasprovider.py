from ubuntui.dialog import opts_to_ui, Dialog
from ubuntui.ev import EventLoop
from conjure.models.jujumodels.maas import MaasJujuModel


class MaasJujuModelView(Dialog):
    input_items = opts_to_ui(MaasJujuModel.config)

    def __init__(self, common, cb):
        self.common = common
        title = "MAAS Credentials"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
