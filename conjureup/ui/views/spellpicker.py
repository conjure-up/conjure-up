from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR


class SpellPickerWidget(WidgetWrap):

    def __init__(self, spell, cb):
        self._spell = spell
        self.cb = cb
        super().__init__(self.build_widget())

    def build_widget(self):
        """ Provides a rendered spell widget suitable for pile
        """
        return Color.body(
            menu_btn(label=self._spell['name'],
                     on_press=self.cb,
                     user_data=self._spell),
            focus_map='menu_button focus'
        )


class SpellPickerView(WidgetWrap):

    def __init__(self, app, spells, cb):
        self.app = app
        self.cb = cb
        self.spells = [SpellPickerWidget(spell, self.submit)
                       for spell in spells]
        self.config = self.app.config
        self.frame = Frame(body=self._build_widget(),
                           footer=self._build_footer())
        super().__init__(self.frame)
        self.handle_focus_changed()

    def keypress(self, size, key):
        rv = super().keypress(size, key)
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        self.handle_focus_changed()
        return rv

    def handle_focus_changed(self):
        self.selected_spell_w = None
        fw = self.pile.focus
        if not isinstance(fw, SpellPickerWidget):
            return

        if fw != self.selected_spell_w:
            self.selected_spell_w = fw
            if fw is None:
                self.spell_description.set_text("No spell selected")
            else:
                self.spell_description.set_text(fw._spell['description'])

    def _swap_focus(self):
        self.current_focused_frame = None
        if self.current_focused_frame is None:
            self.current_focused_frame = self.frame.footer
            self.frame.footer.focus_position = 0
        else:
            self.current_focused_frame = self.body.footer
            self.frame.body.focus_position = 0

    def _build_buttons(self):
        cancel = menu_btn(on_press=self.cancel,
                          label="\nQUIT\n")
        buttons = [
            Padding.line_break(""),
            Color.menu_button(cancel,
                              focus_map='button_primary focus')
        ]
        return Pile(buttons)

    def _build_footer(self):
        self.spell_description = Text("")
        footer_pile = Pile([
            Padding.center_80(self.spell_description),
            Padding.line_break(""),
            Color.frame_footer(
                Columns([
                    ('fixed', 2, Text("")),
                    ('fixed', 13, self._build_buttons())
                ]))
        ])
        return footer_pile

    def _build_widget(self):
        total_items = [HR()]
        total_items += [spell for spell in self.spells]
        total_items += [HR()]

        self.pile = Pile(total_items)
        return Padding.center_60(Filler(self.pile, valign='top'))

    def submit(self, btn, result):
        self.cb(result['key'])

    def cancel(self, btn):
        EventLoop.exit(0)
