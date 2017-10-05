from ubuntui.utils import Color
from ubuntui.widgets.hr import HR
from urwid import Columns, Pile, Text

from conjureup.ui.views.base import (
    NEXT_GROUP,
    NEXT_GROUP_SUBMIT,
    PREV_GROUP,
    BaseView
)
from conjureup.ui.widgets.selectors import OptionalRadioList, RadioList


class VSphereSetupView(BaseView):
    title = "VSphere Configuration"

    def __init__(self, datacenter, update_cloud_cb, *args, **kwargs):
        self.update_cloud_cb = update_cloud_cb
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

        self.extend_command_map({
            'page up': PREV_GROUP,
            'page down': NEXT_GROUP,
            'enter': NEXT_GROUP_SUBMIT,
        })

        super().__init__(*args, **kwargs)

    def build_buttons(self):
        return [self.button('SAVE', lambda btn: self.next())]

    def next(self):
        _formatted_vsphere_config = {}
        for k, v in self.vsphere_config.items():
            _formatted_vsphere_config[k] = v.value or ''
        self.update_cloud_cb(_formatted_vsphere_config)

    def keypress(self, size, key):
        command = self._command_map[key]
        if command == PREV_GROUP:
            self.prev_group()
            return
        elif command in (NEXT_GROUP, NEXT_GROUP_SUBMIT):
            self.next_group(command == NEXT_GROUP_SUBMIT)
            return
        else:
            return super().keypress(size, key)

    def prev_group(self):
        if self.pile.focus_position > 2:
            self.pile.focus_position -= 2

    def next_group(self, submit=False):
        try:
            self.pile.focus_position += 2
        except IndexError:
            if submit:
                self.next()

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
