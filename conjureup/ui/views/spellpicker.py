from ubuntui.ev import EventLoop
from ubuntui.utils import Color
from ubuntui.widgets.buttons import menu_btn
from urwid import Text, WidgetWrap

from conjureup.ui.views.base import BaseView
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
        brmv = BundleReadmeView(self.app.metadata_controller,
                                spellname, spelldir,
                                self.hide_readme,
                                int(rows * .75))
        self.app.ui.set_header("Spell Readme")
        self.app.ui.set_body(brmv)
        # brmv.show()

    def hide_readme(self):
        self.show()

    @property
    def selected_spell(self):
        fw = self.widget.focus
        if isinstance(fw, SpellPickerWidget):
            return fw.spell
        else:
            return None

    def update_spell_description(self):
        spell = self.selected_spell
        if spell:
            self.set_footer(spell['description'])
        else:
            self.set_footer("No spell selected")

    def after_keypress(self):
        self.update_spell_description()

    def build_widget(self):
        total_items = []
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

        return total_items

    def next_screen(self):
        self.cb(self.selected_spell['key'])
