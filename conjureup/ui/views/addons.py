from operator import attrgetter

from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR
from urwid import Columns, Text

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import CheckList


class AddonsView(BaseView):
    title = 'Add-on Selection'
    subtitle = 'Choose one or more additional components to add to your spell'
    footer = ('Select zero or more add-ons using SPACE, then press ENTER '
              'or select CONTINUE to continue')

    def __init__(self, next, back):
        self.next_screen = next
        self.prev_screen = back or (lambda: None)
        self.choices = CheckList()
        self.show_back_button = back is not None
        super().__init__()

    def build_widget(self):
        self.choices.append(HR())
        for addon in sorted(app.addons.values(), key=attrgetter('name')):
            self.choices.append_option(label=addon.friendly_name,
                                       value=addon.name,
                                       state=addon.name in app.selected_addons)
            self.choices.append(Padding.line_break(""))
            self.choices.append(
                Columns([
                    ('fixed', 3, Text('')),
                    Text(addon.description)
                ], dividechars=5)
            )
            self.choices.append(HR())
        if app.addons:
            self.choices.focus_position = 1
        return self.choices

    def build_buttons(self):
        return [
            self.button('CONTINUE', self.next_screen)
        ]

    @property
    def selected(self):
        return self.choices.selected
