from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.controllers.clouds.common import (
    parse_blacklist,
    parse_whitelist
)
from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR


class CloudView(WidgetWrap):

    def __init__(self, app, clouds, cb=None):
        self.app = app
        self.cb = cb
        self.clouds = clouds
        self.blacklist = parse_blacklist()
        self.whitelist = parse_whitelist()
        self.config = self.app.config
        self.buttons_pile_selected = False
        self.frame = Frame(body=self._build_widget(),
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

    def _build_widget(self):
        total_items = []
        clouds = [x for x in self.clouds if 'localhost' != x]
        if len(clouds) > 0:
            total_items.append(Text("Choose a Cloud"))
            total_items.append(HR())
            for item in clouds:
                total_items.append(
                    Color.body(
                        menu_btn(label=item,
                                 on_press=self.submit),
                        focus_map='menu_button focus'
                    )
                )
            total_items.append(Padding.line_break(""))
        total_items.append(Text("Configure a New Cloud"))
        total_items.append(HR())
        if self.whitelist:
            new_clouds = self.whitelist
        elif self.blacklist:
            # TODO: add vsphere
            new_clouds = set(['localhost', 'maas']) ^ set(
                self.blacklist)
        else:
            # TODO: add vsphere
            new_clouds = ['localhost', 'maas']
        for item in new_clouds:
            total_items.append(
                Color.body(
                    menu_btn(label=item,
                             on_press=self.submit),
                    focus_map='menu_button focus'
                )
            )
        return Padding.center_80(Filler(Pile(total_items), valign='top'))

    def submit(self, result):
        self.cb(result.label)

    def cancel(self, btn):
        EventLoop.exit(0)
