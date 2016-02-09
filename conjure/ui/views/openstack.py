from ubuntui.ev import EventLoop
from ubuntui.dialog import opts_to_ui, Dialog
from conjure.models.jujumodels.openstack import OpenStackJujuModel


class OpenStackJujuModelView(Dialog):

    input_items = opts_to_ui(OpenStackJujuModel.config)

    def __init__(self, common, cb):
        self.common = common
        title = "OpenStack Credentials"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
