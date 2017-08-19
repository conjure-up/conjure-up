from pathlib import Path

import yaml
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
        addons_dir = Path(app.config['spell-dir']) / 'addons'
        for addon in sorted(addons_dir.glob('*')):
            metadata = yaml.safe_load((addon / 'metadata.yaml').read_text())
            self.choices.append(CheckBoxValued(metadata.get('friendly-name',
                                                            addon.name),
                                               value=addon.name))
            self.choices.append(Padding.line_break(""))
            self.choices.append(
                Columns([
                    ('fixed', 3, Text('')),
                    Text(metadata.get('description', ''))
                ], dividechars=5)
            )
        return self.choices

    def build_buttons(self):
        return [
            self.button('CONTINUE', lambda btn: self.next())
        ]

    @property
    def selected(self):
        return [choice.value for choice in self.choices
                if isinstance(choice, CheckBoxValued) and choice.state]
