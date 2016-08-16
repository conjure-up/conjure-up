from ubuntui.widgets.buttons import (confirm_btn, cancel_btn)
from ubuntui.widgets.text import Instruction
from ubuntui.utils import Color, Padding
from ubuntui.widgets.hr import HR
from urwid import (WidgetWrap, Pile, Text, Columns, Filler)
from collections import OrderedDict
from ubuntui.widgets.input import (StringEditor, YesNo)
# import os

# Network format
#
# { key: (Widget, Help Text)}

NETWORK = OrderedDict([
    ('_USE_LXD_BRIDGE',
     (YesNo(),
      'Use a new bridge')),
    ('LXD_BRIDGE',
     (StringEditor(default='lxdbr0'),
      'Bridge name')),
    # ('_LXD_CONFILE',
    #  (StringEditor(),
    #   None)),
    ('LXD_DOMAIN',
     (StringEditor(default='lxd'),
      'DNS domain for the bridge')),
    ('LXD_IPV4_ADDR',
     (StringEditor(default='10.10.0.1'),
      'IPv4 Address (e.g. 10.10.0.1)')),
    ('LXD_IPV4_NETMASK',
     (StringEditor(default='255.255.255.0'),
      'IPv4 netmask (e.g. 255.255.255.0)')),
    ('LXD_IPV4_NETWORK',
     (StringEditor(default='10.10.0.1/24'),
      'IPv4 network (e.g. 10.10.0.1/24)')),
    ('LXD_IPV4_DHCP_RANGE',
     (StringEditor(default='10.10.0.2,10.10.0.254'),
      'IPv4 DHCP range (e.g. 10.10.0.2,10.10.0.254)')),
    ('LXD_IPV4_DHCP_MAX',
     (StringEditor(default='250'),
      'IPv4 DHCP number of hosts (e.g. 250)')),
    ('LXD_IPV4_NAT',
     (YesNo(),
      'NAT IPv4 traffic'))
    # Enable this at some point
    # ('_LXD_IPV6_ADDR',
    #  (StringEditor(),
    #   None)),
    # ('_LXD_IPV6_MASK',
    #  (StringEditor(),
    #   None)),
    # ('_LXD_IPV6_NETWORK',
    #  (StringEditor(),
    #   None)),
    # ('_LXD_IPV6_NAT',
    #  (YesNo(),
    #   None)),
    # ('_LXD_IPV6_PROXY',
    #  (YesNo(),
    #   None))
])


class LXDSetupView(WidgetWrap):
    def __init__(self, app, cb):
        self.app = app
        self.input_items = NETWORK
        self.cb = cb
        _pile = [
            # Padding.center_60(Instruction(
            #     "Enter LXD information:")),
            Padding.center_60(Instruction(
                "Please configure networking for LXD"
            )),
            Padding.center_60(HR()),
            Padding.center_60(self.build_info()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="middle"))

    def _swap_focus(self):
        if self._w.body.focus_position == 2:
            self._w.body.focus_position = 4
        else:
            self._w.body.focus_position = 2

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def buttons(self):
        confirm = confirm_btn(on_press=self.submit)
        cancel = cancel_btn(on_press=self.cancel)

        buttons = [
            Color.button_primary(confirm, focus_map='button_primary focus'),
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_info(self):
        items = [
            Text("There was no LXD bridge found on your system "
                 "which usually means this is your first time running "
                 "LXD."),
            Padding.line_break(""),
            # Text("If you wish to do so now pressing confirm will drop you out "  # noqa
            #      "of the installer and walk you through configuring your "
            #      "network for LXD. Once complete the installer will "
            #      "start again from the beginning where you can choose "
            #      "to deploy the bundle via LXD.")
            Text("If you wish to do so now pressing confirm will drop you out "
                 "of the installer and you will be required to run "
                 "`lxd init` to configure the network for LXD. Once complete "
                 "re-run conjure-up and continue the installation.")

        ]
        return Pile(items)

    def build_inputs(self):
        # FIXME: Skip this for now as we're shelling out to
        # dpkg-reconfigure lxd :\ yay and such.
        items = []
        for k in self.input_items.keys():
            widget, help_text = self.input_items[k]
            if isinstance(widget.value, bool):
                widget.set_default('Yes', True)
            if k.startswith('_'):
                # Don't treat 'private' keys as input
                continue
            col = Columns(
                [
                    ('weight', 0.5, Text(help_text, align='right')),
                    Color.string_input(widget,
                                       focus_map='string_input focus')
                ], dividechars=1
            )
            items.append(col)
            items.append(Padding.line_break(""))
        return Pile(items)

    def cancel(self, btn):
        self.cb(back=True)

    def submit(self, result):
        # os.execl("/usr/share/conjure-up/run-lxd-config",
        #          "/usr/share/conjure-up/run-lxd-config",
        #          self.app.config['spell'])
        self.cb(needs_lxd_setup=True)
