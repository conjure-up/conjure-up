from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.ui.views.bundle_readme_view import BundleReadmeView


class SpellPickerWidget(WidgetWrap):

    def __init__(self, spell, cb):
        self.spell = spell
        self.cb = cb
        super().__init__(self.build_widget())

    def build_widget(self):
        """ Provides a rendered spell widget suitable for pile
        """
        return Color.body(
            menu_btn(label=self.spell['name'],
                     on_press=self.cb,
                     user_data=self.spell),
            focus_map='menu_button focus'
        )


class SpellPickerView(WidgetWrap):

    def __init__(self, app, spells, cb):
        self.app = app
        self.cb = cb
        self.spells = spells
        self.config = self.app.config
        self.frame = Frame(body=self._build_widget(),
                           footer=self._build_footer())

        self.buttons_pile_selected = False

        super().__init__(self.frame)
        self.handle_focus_changed()

    def keypress(self, size, key):
        rv = super().keypress(size, key)
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        self.handle_focus_changed()
        if key in ['r'] and self.selected_spell_w is not None:
            _, rows = EventLoop.screen_size()
            cur_spell = self.selected_spell_w.spell
            spellname = cur_spell['name']
            spelldir = cur_spell['spell-dir']
            brmv = BundleReadmeView(self.app.metadata_controller,
                                    spellname, spelldir,
                                    self.handle_readme_done,
                                    int(rows * .75))
            self.app.ui.set_header("Spell Readme")
            self.app.ui.set_body(brmv)
        return rv

    def handle_readme_done(self):
        self.app.ui.set_body(self)

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
                self.spell_description.set_text(fw.spell['description'])

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
                              focus_map='button_primary focus')
        ]
        self.buttons_pile = Pile(buttons)
        return self.buttons_pile

    def _build_footer(self):
        self.spell_description = Text("")
        footer_pile = Pile([
            Padding.center_60(self.spell_description),
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
        prev_cat = None
        for category, spell in self.spells:
            if category == "_unassigned_spells":
                category = "other"
            if category != prev_cat:
                if prev_cat:
                    total_items.append(Text(""))
                total_items.append(Color.label(Text(category)))
                prev_cat = category
            total_items.append(SpellPickerWidget(spell, self.submit))
        total_items += [HR()]

        self.pile = Pile(total_items)
        return Padding.center_60(Filler(self.pile, valign='top'))

    def submit(self, btn, result):
        self.cb(result['key'])

    def cancel(self, btn):
        EventLoop.exit(0)
