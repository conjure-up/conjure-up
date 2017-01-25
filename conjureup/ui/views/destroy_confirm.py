from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.text import Instruction


class DestroyConfirmView(WidgetWrap):

    def __init__(self, app, controller, model, cb):
        self.app = app
        self.cb = cb
        self.controller = controller
        self.model = model
        self.config = self.app.config
        self.buttons_pile_selected = False
        self.frame = Frame(body=self._build_widget(),
                           footer=self._build_footer())

        self.frame.focus_position = 'footer'
        self.buttons.focus_position = 1

        super().__init__(self.frame)

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def _swap_focus(self):
        if not self.buttons_pile_selected:
            self.buttons_pile_selected = True
            self.frame.focus_position = 'footer'
            self.buttons.focus_position = 1
        else:
            self.buttons_pile_selected = False
            self.frame.focus_position = 'body'

    def _build_footer(self):
        no = menu_btn(on_press=self.cancel,
                      label="\n  NO\n")
        yes = menu_btn(on_press=self.submit,
                       label="\n  YES\n")
        self.buttons = Columns([
            ('fixed', 2, Text("")),
            ('fixed', 11, Color.menu_button(
                no,
                focus_map='button_primary focus')),
            Text(""),
            ('fixed', 11, Color.menu_button(
                yes,
                focus_map='button_primary focus')),
            ('fixed', 2, Text(""))
        ])

        self.footer = Pile([
            Padding.line_break(""),
            self.buttons
        ])
        return Color.frame_footer(self.footer)

    def _build_widget(self):
        total_items = []
        total_items.append(Instruction("Model Information:"))
        total_items.append(HR())
        total_items.append(Text("Model name: {}".format(
            self.model['name'])))
        total_items.append(Text("Controller name: {}".format(
            self.model['controller-name'])))
        total_items.append(Text("Cloud: {}".format(
            self.model['cloud'])))
        total_items.append(Text("Status: {}".format(
            self.model['status']['current'])))
        total_items.append(Text("Online since: {}".format(
            self.model['status']['since'])))
        total_items.append(HR())
        return Padding.center_80(Filler(Pile(total_items), valign='top'))

    def submit(self, btn):
        self.footer.contents[-1] = (Text(""), self.footer.options())
        self.cb(self.controller, self.model['name'])

    def cancel(self, btn):
        self.cb(None, None)
