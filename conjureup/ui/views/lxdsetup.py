from ubuntui.utils import Color
from ubuntui.widgets.hr import HR
from urwid import Columns, Text

from conjureup import errors
from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import RadioList


class LXDSetupView(BaseView):
    title = "LXD Configuration"
    subtitle = "Select a network bridge and storage pool for this deployment"

    def __init__(self, devices, submit_cb, back_cb):
        self.devices = devices
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        self.lxd_config = {
            'network': RadioList(self.devices['networks'].keys()),
            'storage-pool': RadioList(self.devices['storage-pools'].keys()),
        }

        if not self.devices['networks']:
            raise errors.LXDNetworkError()
        if not self.devices['storage-pools']:
            raise errors.LXDStorageError()

        super().__init__()

    def build_buttons(self):
        return [self.button('SAVE', self.submit)]

    def submit(self):
        network = self.lxd_config['network'].selected
        storage_pool = self.lxd_config['storage-pool'].selected
        self.submit_cb(self.devices['networks'][network],
                       self.devices['storage-pools'][storage_pool])

    def build_widget(self):
        return [
            Columns([
                ('fixed', 16, Text('network bridge', align="right")),
                Color.string_input(
                    self.lxd_config['network'],
                    focus_map='string_input focus')
            ], dividechars=1),
            HR(),
            Columns([
                ('fixed', 16, Text('storage pool', align="right")),
                Color.string_input(
                    self.lxd_config['storage-pool'],
                    focus_map='string_input focus')
            ], dividechars=1),
        ]
