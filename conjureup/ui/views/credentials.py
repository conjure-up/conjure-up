from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR
from urwid import Text

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView, SchemaFormView
from conjureup.ui.widgets.select_list import SelectorList


class NewCredentialView(SchemaFormView):
    title = "New Credential Creation"

    def __init__(self, *args, **kwargs):
        cloud_type = app.provider.cloud_type.upper()
        self.header = "Enter your {} credentials:".format(cloud_type)
        super().__init__(*args, **kwargs)


class CredentialPickerView(BaseView):
    title = "Choose a Credential"
    subtitle = "Please select an existing credential, " \
               "or choose to add a new one."
    footer = 'Please press [ENTER] on highlighted credential to proceed.'

    def __init__(self, credentials, default, select_cb, new_cb,
                 *args, **kwargs):
        if default:
            # sort the default cred to the top
            credentials.remove(default)
            credentials.insert(0, default)

        self.credentials = credentials
        self.new_cb = new_cb
        self.select_cb = select_cb
        super().__init__(*args, **kwargs)

    def build_widget(self):
        return [
            Text("Choose a Credential"),
            HR(),
            SelectorList(self.credentials, self.select_cb),
            Padding.line_break(""),
            HR(),
            SelectorList(["Add a new credential"], lambda _: self.new_cb()),
        ]
