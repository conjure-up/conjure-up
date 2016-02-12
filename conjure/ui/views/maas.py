from ubuntui.dialog import opts_to_ui, Dialog
from ubuntui.ev import EventLoop


class MaasJujuModelView(Dialog):

    def __init__(self, common, cb):
        self.common = common
        self.config = self.common['config']
        self.input_items = opts_to_ui(self.config['juju-models']['maas'])
        title = "MAAS Credentials"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
