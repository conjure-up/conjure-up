from operator import attrgetter

from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR
from urwid import CheckBox, Columns, Text

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView


class CheckBoxValued(CheckBox):
    """
    Subclass of CheckBox that associates a value with the checkbox.
    """

    def __init__(self, label, value, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.value = value


class AddonsView(BaseView):
    title = 'Add-on Selection'
    subtitle = 'Choose one or more additional components to add to your spell'

    def __init__(self, next, back):
        self.next = next
        self.choices = []
        super().__init__(back)

    def build_widget(self):
        self.choices.append(HR())
        for addon in sorted(app.addons.values(), key=attrgetter('name')):
            self.choices.append(CheckBoxValued(addon.friendly_name,
                                               value=addon.name))
            self.choices.append(Padding.line_break(""))
            self.choices.append(
                Columns([
                    ('fixed', 3, Text('')),
                    Text(addon.description)
                ], dividechars=5)
            )
            self.choices.append(HR())
        return self.choices

    def build_buttons(self):
        return [
            self.button('CONTINUE', lambda btn: self.next())
        ]

    @property
    def selected(self):
        return [choice.value for choice in self.choices
                if isinstance(choice, CheckBoxValued) and choice.state]
