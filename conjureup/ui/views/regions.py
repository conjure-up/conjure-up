from ubuntui.widgets.hr import HR
from urwid import Text

from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.select_list import SelectorList


class RegionPickerView(BaseView):
    title = 'Choose a Region'
    subtitle = 'Please select from a list of available regions'
    footer = 'Please press [ENTER] on highlighted region to proceed.'

    def __init__(self, regions, default, submit_cb, *args, **kwargs):
        if default:
            # sort the default cred to the top
            regions.remove(default)
            regions.insert(0, default)

        self.regions = regions
        self.submit_cb = submit_cb
        super().__init__(*args, **kwargs)

    def build_widget(self):
        return [
            Text("Choose a Region"),
            HR(),
            SelectorList(self.regions, self.submit_cb),
        ]

    def submit(self, result):
        self.submit_cb(result.label)
