from ubuntui.utils import Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import SelectorHorizontal
from urwid import Columns, Text

from conjureup.ui.views.base import BaseView


class LXDSetupViewError(Exception):
    pass


class LXDSetupView(BaseView):
    title = "LXD Configuration"
    subtitle = "Select a network bridge and storage pool for this deployment"

    def __init__(self, devices, submit_cb, back_cb):
        self.devices = devices
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        self.lxd_config = {
            'network': SelectorHorizontal(
                [net for net in self.devices['networks'].keys()]
            ),
            'storage-pool': SelectorHorizontal(
                [pool for pool in self.devices['storage-pools'].keys()]
            )
        }

        try:
            self.lxd_config['network'].set_default(
                self.lxd_config['network'].group[0].label, True
            )

            self.lxd_config['storage-pool'].set_default(
                self.lxd_config['storage-pool'].group[0].label, True
            )
        except IndexError:
            raise LXDSetupViewError(
                "Could not locate any network or storage "
                "devices to continue. Please make sure you "
                "have at least 1 network bridge and 1 storage "
                "pool: see `lxc network list` and "
                "`lxc storage list`.  \n\n"
                "Also note that the network bridge must not have "
                "ipv6 enabled, to disable run `lxc network set "
                "lxdbr0 ipv6.address none ipv6.nat false`")
        super().__init__()

    def build_buttons(self):
        return [self.button('SAVE', self.submit)]

    def submit(self):
        network = self.lxd_config['network'].value
        storage_pool = self.lxd_config['storage-pool'].value
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
