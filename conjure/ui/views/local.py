from ubuntui.dialog import Dialog, opts_to_ui
from ubuntui.ev import EventLoop


class LocalJujuModelView(Dialog):

    def __init__(self, common, cb):
        self.common = common
        self.config = self.common['config']
        self.input_items = opts_to_ui(self.config['juju-models']['local'])
        title = "Local Configuration"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
