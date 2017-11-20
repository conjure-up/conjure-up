from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from urwid import BoxAdapter, Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup import events, juju
from conjureup.consts import CUSTOM_PROVIDERS, cloud_types


class CloudWidget(WidgetWrap):
    default_enabled_msg = 'Press [ENTER] to select this cloud, or use the ' \
                          'arrow keys to select another cloud.'
    default_disabled_msg = 'This cloud is disabled due to your selection of ' \
                           'spell or add-on. Please use the arrow keys to ' \
                           'select another cloud.'

    def __init__(self,
                 name,
                 cb,
                 enabled=True,
                 enabled_msg=None,
                 disabled_msg=None):
        self.name = name
        self._enabled_widget = Color.body(
            menu_btn(label=self.name,
                     on_press=cb),
            focus_map='menu_button focus'
        )
        self._disabled_widget = Color.info_context(
            menu_btn(
                label=name,
                on_press=None),
            focus_map='disabled_button'
        )
        self.enabled_msg = enabled_msg or self.default_enabled_msg
        self.disabled_msg = disabled_msg or self.default_disabled_msg
        self._enabled = enabled
        super().__init__(self._enabled_widget if enabled
                         else self._disabled_widget)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self._w = self._enabled_widget if enabled else self._disabled_widget


class CloudView(WidgetWrap):
    lxd_unavailable_msg = ("LXD not found, please install and wait "
                           "for this message to disappear:\n\n"
                           "  $ sudo snap install lxd\n"
                           "  $ sudo usermod -a -G lxd <youruser>\n"
                           "  $ newgrp lxd\n"
                           "  $ /snap/bin/lxd init --auto\n"
                           "  $ /snap/bin/lxc network create lxdbr0 "
                           "ipv4.address=auto ipv4.nat=true "
                           "ipv6.address=none ipv6.nat=false ")

    def __init__(self, app, public_clouds, custom_clouds,
                 compatible_cloud_types, cb=None):
        self.app = app
        self.cb = cb
        self.public_clouds = public_clouds
        self.custom_clouds = custom_clouds
        self.compatible_cloud_types = compatible_cloud_types
        self.config = self.app.config
        self.buttons_pile_selected = False
        self.items = Pile([])
        self.message = Text('')
        self._items_localhost_idx = None

        self.frame = Frame(
            body=Padding.center_80(
                Filler(self._build_widget(), valign='top')),
            footer=self._build_footer())
        super().__init__(self.frame)

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        result = super().keypress(size, key)
        self.update_message()
        return result

    def update_message(self):
        selected = self.items.focus
        if selected.enabled:
            msg = selected.enabled_msg
        else:
            msg = selected.disabled_msg
        self.message.set_text(msg)

    def _swap_focus(self):
        if not self.buttons_pile_selected:
            self.buttons_pile_selected = True
            self.frame.focus_position = 'footer'
            self.buttons_pile.focus_position = 1
        else:
            self.buttons_pile_selected = False
            self.frame.focus_position = 'body'

    def _build_buttons(self):
        cancel = menu_btn(on_press=self.cancel,
                          label="\n  QUIT\n")
        buttons = [
            Padding.line_break(""),
            Color.menu_button(cancel,
                              focus_map='button_primary focus'),
        ]
        self.buttons_pile = Pile(buttons)
        return self.buttons_pile

    def _build_footer(self):
        footer_pile = Pile([
            Padding.center_90(HR()),
            Color.body(BoxAdapter(Filler(Columns([
                Text(''),
                ('pack', self.message),
                Text(''),
            ]), valign='bottom'), 7)),
            Padding.line_break(""),
            Color.frame_footer(
                Columns([
                    ('fixed', 2, Text("")),
                    ('fixed', 13, self._build_buttons())
                ])),
        ])
        self.update_message()
        return footer_pile

    def _enable_localhost_widget(self):
        """ Sets the proper widget for localhost availability
        """
        if self._items_localhost_idx is None:
            return
        self.items.contents[self._items_localhost_idx][0].enabled = True
        self.update_message()

    def _add_item(self, item):
        self.items.contents.append((item, self.items.options()))

    def _build_widget(self):
        default_selection = None
        cloud_types_by_name = juju.get_cloud_types_by_name()
        if len(self.public_clouds) > 0:
            self._add_item(Text("Public Clouds"))
            self._add_item(HR())
            for cloud_name in self.public_clouds:
                cloud_type = cloud_types_by_name[cloud_name]
                allowed = cloud_type in self.compatible_cloud_types
                if allowed and default_selection is None:
                    default_selection = len(self.items.contents)
                self._add_item(
                    CloudWidget(name=cloud_name,
                                cb=self.submit,
                                enabled=allowed)
                )
            self._add_item(Padding.line_break(""))
        if len(self.custom_clouds) > 0:
            self._add_item(Text("Your Clouds"))
            self._add_item(HR())
            for cloud_name in self.custom_clouds:
                cloud_type = cloud_types_by_name[cloud_name]
                allowed = cloud_type in self.compatible_cloud_types
                if allowed and default_selection is None:
                    default_selection = len(self.items.contents)
                self._add_item(
                    CloudWidget(name=cloud_name,
                                cb=self.submit,
                                enabled=allowed)
                )
            self._add_item(Padding.line_break(""))
        new_clouds = juju.get_compatible_clouds(CUSTOM_PROVIDERS)
        if new_clouds:
            lxd_allowed = cloud_types.LOCALHOST in self.compatible_cloud_types
            self._add_item(Text("Configure a New Cloud"))
            self._add_item(HR())
            for cloud_type in sorted(CUSTOM_PROVIDERS):
                if cloud_type == cloud_types.LOCALHOST and lxd_allowed:
                    self._items_localhost_idx = len(self.items.contents)
                    if default_selection is None:
                        default_selection = len(self.items.contents)
                    self._add_item(
                        CloudWidget(name=cloud_type,
                                    cb=self.submit,
                                    enabled=events.LXDAvailable.is_set(),
                                    disabled_msg=self.lxd_unavailable_msg)
                    )
                else:
                    allowed = cloud_type in self.compatible_cloud_types
                    if allowed and default_selection is None:
                        default_selection = len(self.items.contents)
                    self._add_item(
                        CloudWidget(name=cloud_type,
                                    cb=self.submit,
                                    enabled=allowed)
                    )

        self.items.focus_position = default_selection or 2
        return self.items

    def submit(self, result):
        self.cb(result.label)

    def cancel(self, btn):
        EventLoop.exit(0)
