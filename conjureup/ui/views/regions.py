from ubuntui.widgets.hr import HR
from urwid import Text

from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.select_list import SelectorList


class RegionPickerView(BaseView):
    title = 'Choose a Region'
    subtitle = "Please select from the list of available regions."
    footer = 'Please press [ENTER] on highlighted region to proceed.'

    def __init__(self, regions, default, submit_cb, back_cb):
        self.submit_cb = submit_cb
        self.prev_screen = back_cb

        if default:
            # sort the default cred to the top
            regions.remove(default)
            regions.insert(0, default)

        self.regions = regions
        super().__init__()

    def build_widget(self):
        return SelectorList(self.regions)

    def submit(self):
        self.submit_cb(self.widget.selected)
