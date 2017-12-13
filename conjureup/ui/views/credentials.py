from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR

from conjureup.app_config import app
from conjureup.ui.views.base import BaseView, SchemaFormView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


NEW_CRED = Ellipsis  # placeholder for new credential


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

    def __init__(self, credentials, default, select_cb, new_cb, back_cb):
        if default and default in credentials:
            # sort the default cred to the top
            credentials.remove(default)
            credentials.insert(0, default)

        self.credentials = credentials
        self.new_cb = new_cb
        self.select_cb = select_cb
        self.prev_screen = back_cb
        super().__init__()

    def build_widget(self):
        widget = MenuSelectButtonList(self.credentials)
        widget.append(Padding.line_break(""))
        widget.append(HR())
        widget.append_option("Add a new credential", NEW_CRED)
        return widget

    def submit(self):
        value = self.widget.selected
        if value is NEW_CRED:
            self.new_cb()
        else:
            self.select_cb(value)
