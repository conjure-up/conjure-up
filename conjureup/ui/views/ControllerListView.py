from collections import defaultdict
from functools import partial

from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR


class ControllerListView(WidgetWrap):

    def __init__(self, app, controllers, cb):
        self.app = app
        self.cb = cb
        self.controllers = controllers
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
        if len(self.controllers) > 0:
            total_items.append(HR())
            cdict = defaultdict(lambda: defaultdict(list))
            for cname, d in self.controllers.items():
                cdict[d['cloud']][d.get('region', None)].append(cname)

            for cloudname, cloud_d in sorted(cdict.items()):
                total_items.append(Color.label(
                    Text("  {}".format(cloudname))))
                for regionname, controllers in cloud_d.items():
                    for controller in sorted(controllers):
                        label = "    {}".format(controller)
                        if regionname:
                            label += " ({})".format(regionname)
                        total_items.append(
                            Color.body(
                                menu_btn(label=label,
                                         on_press=partial(self.submit,
                                                          controller)),
                                focus_map='menu_button focus'
                            )
                        )
                total_items.append(Padding.line_break(""))
            total_items.append(Padding.line_break(""))
        total_items.append(HR())
        total_items.append(
            Color.body(
                menu_btn(label="Create New",
                         on_press=self.handle_create_new),
                focus_map='menu_button focus'
            )
        )
        return Padding.center_80(Filler(Pile(total_items), valign='top'))

    def submit(self, cname, btn):
        self.cb(cname)

    def handle_create_new(self, btn):
        self.cb(None)

    def cancel(self, btn):
        EventLoop.exit(0)
