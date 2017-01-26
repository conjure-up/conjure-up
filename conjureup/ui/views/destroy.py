from functools import partial

from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn


class DestroyView(WidgetWrap):

    def __init__(self, app, models, cb):
        self.app = app
        self.cb = cb
        self.controllers = models.keys()
        self.models = models
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
        for controller in self.controllers:
            models = self.models[controller]['models']
            if len(models) > 0:
                total_items.append(Color.label(
                    Text("{} ({})".format(controller,
                                          models[0].get('cloud', "")))
                ))
                for model in models:
                    if model['name'] == "controller":
                        continue
                    label = ("  {}, Machine Count: {}, "
                             "Running since: {}".format(
                                 model['name'],
                                 len(model['machines'].keys()),
                                 model['status']['since']))
                    total_items.append(
                        Color.body(
                            menu_btn(label=label,
                                     on_press=partial(self.submit,
                                                      controller,
                                                      model)),
                            focus_map='menu_button focus'
                        ))
                total_items.append(Padding.line_break(""))
            total_items.append(Padding.line_break(""))
        return Padding.center_80(Filler(Pile(total_items), valign='top'))

    def submit(self, controller, model, btn):
        self.cb(controller, model)

    def cancel(self, btn):
        EventLoop.exit(0)
