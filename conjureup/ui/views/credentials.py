from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView, SchemaFormView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class NewCredentialView(SchemaFormView):
    title = "New Credential Creation"

    def __init__(self, *args, **kwargs):
        cloud_type = app.provider.cloud_type.upper()
        self.subtitle = "Enter your {} credentials".format(cloud_type)
        super().__init__(*args, **kwargs)


class CredentialPickerView(BaseView):
    title = "Choose a Credential"
    subtitle = "Please select an existing credential, " \
               "or choose to add a new one."
    footer = 'Please press [ENTER] on highlighted credential to proceed.'

    def __init__(self, credentials, default, submit_cb, back_cb):
        self.credentials = credentials
        self.default = default
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        super().__init__()

    def build_widget(self):
        widget = MenuSelectButtonList(self.credentials, self.default)
        widget.append(Padding.line_break(""))
        widget.append(HR())
        widget.append_option("Add a new credential", None)
        return widget

    def submit(self):
        self.submit_cb(self.widget.selected)
