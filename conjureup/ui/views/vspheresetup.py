from ubuntui.utils import Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import SelectorHorizontal
from urwid import Columns, Pile, Text

from conjureup.ui.views.base import BaseView


class VSphereSetupView(BaseView):
    title = "VSphere Configuration"

    def __init__(self, datacenter, update_cloud_cb, *args, **kwargs):
        self.update_cloud_cb = update_cloud_cb
        self.datacenter = datacenter
        self.vsphere_config = {
            'primary-network': SelectorHorizontal(
                [net.name for net in self.datacenter.network]),
            'external-network': SelectorHorizontal(
                [net.name for net in self.datacenter.network]),
            'datastore': SelectorHorizontal(
                [ds.name for ds in self.datacenter.datastore])
        }

        # Set defaults
        self.vsphere_config['primary-network'].set_default(
            self.vsphere_config['primary-network'].group[0].label, True)
        self.vsphere_config['datastore'].set_default(
            self.vsphere_config['datastore'].group[0].label, True)

        super().__init__(*args, **kwargs)

    def build_buttons(self):
        return [self.button('SAVE', self.submit)]

    def submit(self, result):
        _formatted_vsphere_config = {}
        for k, v in self.vsphere_config.items():
            _formatted_vsphere_config[k] = v.value
        self.update_cloud_cb(_formatted_vsphere_config)

    def build_widget(self):
        rows = [
            Text("Select primary/external network, "
                 "and datastore for this deployment:"),
            HR(),
            Columns([
                ('weight', 0.5, Text('primary network', align="right")),
                Color.string_input(
                    self.vsphere_config['primary-network'],
                    focus_map='string_input focus')
            ], dividechars=1),
            HR(),
            Columns([
                ('weight', 0.5, Text('external network (optional)',
                                     align="right")),
                Color.string_input(
                    self.vsphere_config['external-network'],
                    focus_map='string_input focus')
            ], dividechars=1),
            HR(),
            Columns([
                ('weight', 0.5, Text('datastore', align="right")),
                Color.string_input(
                    self.vsphere_config['datastore'],
                    focus_map='string_input focus')
            ], dividechars=1)
        ]
        self.pile = Pile(rows)
        return self.pile
