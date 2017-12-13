from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class RegionPickerView(BaseView):
    title = 'Choose a Region'
    subtitle = "Please select from the list of available regions."
    footer = 'Please press [ENTER] on highlighted region to proceed.'

    def __init__(self, regions, default, submit_cb, back_cb):
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        self.regions = regions
        self.default = default
        super().__init__()

    def build_widget(self):
        return MenuSelectButtonList(self.regions, self.default)

    def submit(self):
        self.submit_cb(self.widget.selected)
