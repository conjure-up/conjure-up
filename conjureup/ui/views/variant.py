from __future__ import unicode_literals
from urwid import (WidgetWrap, Text, Pile,
                   Columns, Filler)
from ubuntui.widgets.buttons import (quit_btn, menu_btn)
from ubuntui.utils import Color, Padding
from ubuntui.ev import EventLoop
from conjureup.utils import pollinate
from conjureup.app_config import app


class VariantView(WidgetWrap):
    def __init__(self, cb):
        self.cb = cb
        self.fname_id_map = {}
        self.current_focus = 2
        _pile = [
            Padding.line_break(""),
            Padding.center_90(self.build_menuable_items()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))

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
        cancel = quit_btn(on_press=self.cancel)

        buttons = [
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_menuable_items(self):
        """ Builds a list of bundles available to install
        """
        cols = []
        for bundle in app.bundles:
            bundle_metadata = bundle['Meta']['bundle-metadata']
            try:
                conjure_data = bundle['Meta']['extra-info/conjure-up']
                name = conjure_data.get('friendly-name',
                                        bundle['Meta']['id']['Name'])
            except KeyError:
                name = bundle['Meta']['id']['Name']
            self.fname_id_map[name] = bundle
            cols.append(
                Columns(
                    [
                        ("weight", 0.2, Color.body(
                            menu_btn(label=name,
                                     on_press=self.done),
                            focus_map="menu_button focus")),
                        ("weight", 0.3, Text(
                            bundle_metadata.get('Description',
                                                'Needs a description'),
                            align="left"))
                    ],
                    dividechars=1
                )
            )
            cols.append(Padding.line_break(""))
        return Pile(cols)

    def cancel(self, button):
        pollinate(app.session_id, 'UC')
        EventLoop.exit(0)

    def done(self, result):
        self.cb(self.fname_id_map[result.label])
