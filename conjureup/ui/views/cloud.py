from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import MenuSelectButton, menu_btn
from ubuntui.widgets.hr import HR
from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup import juju
from conjureup.consts import PROVIDER_TYPES, cloud_types


class CloudView(WidgetWrap):

    def __init__(self, app, public_clouds, custom_clouds, cb=None):
        self.app = app
        self.cb = cb
        self.public_clouds = public_clouds
        self.custom_clouds = custom_clouds
        self.config = self.app.config
        self.buttons_pile_selected = False
        self.pile = None
        self.pile_localhost_idx = None

        self.frame = Frame(
            body=Padding.center_80(
                Filler(self._build_widget(), valign='top')),
            footer=self._build_footer())
        super().__init__(self.frame)

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

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
            Padding.line_break(""),
            Color.frame_footer(
                Columns([
                    ('fixed', 2, Text("")),
                    ('fixed', 13, self._build_buttons())
                ]))
        ])
        return footer_pile

    def _get_localhost_widget_idx(self):
        """ Returns index in pile where localhost widget resides
        """
        if self.pile_localhost_idx:
            return self.pile_localhost_idx

        else:
            for idx, item in enumerate(self.pile.contents):
                if hasattr(item[0], 'original_widget') and \
                   isinstance(item[0].original_widget, MenuSelectButton) and \
                   item[0].original_widget.get_label() == 'localhost':
                    return idx

    def _enable_localhost_widget(self):
        """ Sets the proper widget for localhost availability
        """
        idx = self._get_localhost_widget_idx()
        widget = Color.body(
            menu_btn(label=cloud_types.LOCALHOST,
                     on_press=self.submit),
            focus_map='menu_button focus'
        )
        self._update_pile_at_idx(idx, widget)
        del self.pile.contents[idx + 1]

    def _update_pile_at_idx(self, idx, item):
        """ In place updates a widget in the self.pile contents
        """
        self.pile_localhost_idx = idx
        self.pile.contents[idx] = (item, self.pile.options())

    def _add_item(self, item):
        if not self.pile:
            self.pile = Pile([item])
        else:
            self.pile.contents.append((item, self.pile.options()))

    def _build_widget(self):
        if len(self.public_clouds) > 0:
            self._add_item(Text("Public Clouds"))
            self._add_item(HR())
            for item in self.public_clouds:
                self._add_item(
                    Color.body(
                        menu_btn(label=item,
                                 on_press=self.submit),
                        focus_map='menu_button focus'
                    )
                )
            self._add_item(Padding.line_break(""))
        if len(self.custom_clouds) > 0:
            self._add_item(Text("Your Clouds"))
            self._add_item(HR())
            for item in self.custom_clouds:
                self._add_item(
                    Color.body(
                        menu_btn(label=item,
                                 on_press=self.submit),
                        focus_map='menu_button focus'
                    )
                )
            self._add_item(Padding.line_break(""))
        new_clouds = juju.get_compatible_clouds(PROVIDER_TYPES)
        if new_clouds:
            self._add_item(Text("Configure a New Cloud"))
            self._add_item(HR())
            for item in sorted(new_clouds):
                if item == 'localhost':
                    self._add_item(
                        Color.info_context(
                            menu_btn(
                                label=cloud_types.LOCALHOST,
                                on_press=None),
                            focus_map='disabled_button'
                        )
                    )
                    self._add_item(
                        Color.info_context(
                            Padding.center_90(
                                Text(
                                    "LXD not found, please install and wait "
                                    "for this message to disappear:\n\n"
                                    "  $ sudo snap install lxd\n"
                                    "  $ /snap/bin/lxd init --auto\n"
                                    "  $ /snap/bin/lxc network create lxdbr0 "
                                    "ipv4.address=auto ipv4.nat=true "
                                    "ipv6.address=none ipv6.nat=false "
                                ))
                        )
                    )
                else:
                    self._add_item(
                        Color.body(
                            menu_btn(label=item,
                                     on_press=self.submit),
                            focus_map='menu_button focus'
                        )
                    )

        self.pile.focus_position = 2
        return self.pile

    def submit(self, result):
        self.cb(result.label)

    def cancel(self, btn):
        EventLoop.exit(0)
