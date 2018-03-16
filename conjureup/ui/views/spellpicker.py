from ubuntui.ev import EventLoop
from ubuntui.utils import Color
from urwid import Text

from conjureup.ui.views.base import BaseView
from conjureup.ui.views.bundle_readme_view import BundleReadmeView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class SpellPickerView(BaseView):
    title = "Spell Selection"
    subtitle = "Choose from this list of recommended spells"
    show_back_button = False

    def __init__(self, app, spells, cb):
        self.app = app
        self.cb = cb
        self.spells = spells
        self.config = self.app.config
        super().__init__()
        self.extend_command_map({
            'r': self.show_readme,
        })
        self.update_spell_description()

    def show_readme(self):
        _, rows = EventLoop.screen_size()
        cur_spell = self.selected_spell
        spellname = cur_spell['name']
        spelldir = cur_spell['spell-dir']
        brmv = BundleReadmeView(spellname, spelldir,
                                self.hide_readme,
                                int(rows * .75))
        self.app.ui.set_header("Spell Readme")
        self.app.ui.set_body(brmv)

    def hide_readme(self):
        self.show()

    @property
    def selected_spell(self):
        return self.widget.selected

    def update_spell_description(self):
        spell = self.selected_spell
        if spell:
            self.set_footer(spell['description'])
        else:
            self.set_footer("No spell selected")

    def after_keypress(self):
        self.update_spell_description()

    def build_widget(self):
        widget = MenuSelectButtonList()
        prev_cat = None
        for category, spell in self.spells:
            if category == "_unassigned_spells":
                category = "other"
            if category != prev_cat:
                if prev_cat:
                    widget.append(Text(""))
                widget.append(Color.label(Text(category)))
                prev_cat = category
            widget.append_option(spell['name'], spell)
        widget.focus_position = 1
        return widget

    def next_screen(self):
        self.cb(self.selected_spell['key'])
