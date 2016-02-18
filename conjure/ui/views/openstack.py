from ubuntui.ev import EventLoop
from ubuntui.dialog import opts_to_ui, Dialog


class OpenStackJujuModelView(Dialog):

    def __init__(self, common, cb):
        self.common = common
        self.config = self.common['config']
        self.input_items = opts_to_ui(self.config['juju-models']['openstack'])
        title = "OpenStack Credentials"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
