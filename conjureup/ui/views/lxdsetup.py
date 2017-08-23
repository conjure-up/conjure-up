from ubuntui.utils import Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import SelectorHorizontal
from urwid import Columns, Pile, Text

from conjureup.ui.views.base import BaseView


class LXDSetupView(BaseView):
    title = "LXD Configuration"

    def __init__(self, devices, cb, *args, **kwargs):
        self.devices = devices
        self.cb = cb
        self.lxd_config = {
            'network': SelectorHorizontal(
                [net['name'] for net in self.devices['networks']]
            ),
            'storage-pool': SelectorHorizontal(
                [pool['name'] for pool in self.devices['storage-pools']]
            )
        }
        self.lxd_config['network'].set_default(
            self.lxd_config['network'].group[0].label, True
        )

        self.lxd_config['storage-pool'].set_default(
            self.lxd_config['storage-pool'].group[0].label, True
        )
        super().__init__(*args, **kwargs)

    def build_buttons(self):
        return [self.button('SAVE', self.submit)]

    def submit(self, result):
        _formatted_lxd_config = {}
        for k, v in self.lxd_config.items():
            _formatted_lxd_config[k] = v.value
        self.cb(_formatted_lxd_config)

    def build_widget(self):
        rows = [
            Text("Select a network bridge and storage pool "
                 "for this deployment:"),
            HR(),
            Columns([
                ('weight', 0.5, Text('network bridge', align="right")),
                Color.string_input(
                    self.lxd_config['network'],
                    focus_map='string_input focus')
            ], dividechars=1),
            HR(),
            Columns([
                ('weight', 0.5, Text('storage pool',
                                     align="right")),
                Color.string_input(
                    self.lxd_config['storage-pool'],
                    focus_map='string_input focus')
            ], dividechars=1),
        ]
        self.pile = Pile(rows)
        return self.pile
