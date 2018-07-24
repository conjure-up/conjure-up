from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class DestroyView(BaseView):
    title = "Destroy"
    subtitle = "Please choose a deployed spell to destroy"
    show_back_button = False

    def __init__(self, app, spells, cb):
        self.app = app
        self.cb = cb
        self.spells = spells
        self.config = self.app.config
        super().__init__()

    def build_widget(self):
        # NB: I dont like this currently, but leaving in for now.
        widget = MenuSelectButtonList()
        for spell in self.spells:
            widget.append_option(spell['spellname'])
        widget.select_first()
        return widget

    def submit(self):
        if self.widget.selected:
            self.cb(self.widget.selected)
