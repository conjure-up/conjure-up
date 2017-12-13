from ubuntui.utils import Color
from ubuntui.widgets.hr import HR
from urwid import Columns, Text

from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import OptionalRadioList, RadioList


class VSphereSetupView(BaseView):
    title = "VSphere Configuration"

    def __init__(self, datacenter, update_cloud_cb, back_cb):
        self.update_cloud_cb = update_cloud_cb
        self.prev_screen = back_cb
        self.datacenter = datacenter
        self.vsphere_config = {
            'primary-network': RadioList(
                [net.name for net in self.datacenter.network]),
            'external-network': OptionalRadioList(
                [net.name for net in self.datacenter.network]),
            'datastore': RadioList(
                [ds.name for ds in self.datacenter.datastore])
        }

        # Set defaults
        self.vsphere_config['primary-network'].select_first_option()
        self.vsphere_config['datastore'].select_first_option()

        super().__init__()

    def build_buttons(self):
        return [self.button('SAVE', self.submit)]

    def submit(self):
        _formatted_vsphere_config = {}
        for k, v in self.vsphere_config.items():
            _formatted_vsphere_config[k] = v.selected or ''
        self.update_cloud_cb(_formatted_vsphere_config)

    def build_widget(self):
        return [
            Text("Select primary/external network, "
                 "and datastore for this deployment:"),
            HR(),
            Columns([
                (29, Text('Primary Network', align="right")),
                Color.string_input(
                    self.vsphere_config['primary-network'],
                    focus_map='string_input focus')
            ], dividechars=1),
            HR(),
            Columns([
                (29, Text('External Network (optional)', align="right")),
                Color.string_input(
                    self.vsphere_config['external-network'],
                    focus_map='string_input focus')
            ], dividechars=1),
            HR(),
            Columns([
                (29, Text('Datastore', align="right")),
                Color.string_input(
                    self.vsphere_config['datastore'],
                    focus_map='string_input focus')
            ], dividechars=1)
        ]
