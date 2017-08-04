from os import path

import yaml

from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.ui.views.credentials import (
    CredentialPickerView,
    NewCredentialView
)

from . import common


class CredentialsController(common.BaseCredentialsController):
    def render(self):
        if app.provider.cloud_type == 'localhost':
            # no credentials required for localhost
            self.finish()
        elif not app.provider.credential:
            self.render_form()
        elif len(self.credentials) >= 1:
            self.render_picker()
        else:
            self.finish()

    def render_form(self):
        view = NewCredentialView(self.save_credential, self.back)
        view.show()

    def render_picker(self):
        view = CredentialPickerView(self.credentials, app.provider.credential,
                                    self.set_credential_from_select,
                                    self.switch, self.back)
        view.show()

    def switch(self):
        self.was_picker = True
        self.render_form()

    def back(self):
        if self.was_picker:
            # if they were on the picker and chose New, BACK should
            # take them back to the picker, not to the cloud selection
            self.was_picker = False
            return self.render_picker()
        return controllers.use('clouds').render()

    def _format_creds(self):
        """ Formats the credentials into strings from the widgets values
        """
        formatted = {}
        formatted['auth-type'] = app.provider.auth_type
        for field in app.provider.form.fields():
            if not field.storable:
                continue
            formatted[field.key] = field.value

        return formatted

    def set_credential_from_select(self, credential_name):
        app.provider.credential = credential_name
        self.finish()

    def save_credential(self):
        cred_path = path.join(utils.juju_path(), 'credentials.yaml')
        app.provider.credential = "conjure-{}-{}".format(app.provider.cloud,
                                                         utils.gen_hash())

        try:
            existing_creds = yaml.safe_load(open(cred_path))
        except:
            existing_creds = {'credentials': {}}

        if app.provider.cloud in existing_creds['credentials'].keys():
            c = existing_creds['credentials'][app.provider.cloud]
            c[app.provider.credential] = self._format_creds()
        else:
            # Handle the case where path exists but an entry for the cloud
            # has yet to be added.
            existing_creds['credentials'][app.provider.cloud] = {
                app.provider.credential: self._format_creds()
            }

        with open(cred_path, 'w') as cred_f:
            cred_f.write(yaml.safe_dump(existing_creds,
                                        default_flow_style=False))

        # Persist input fields in current provider, this is so we
        # can login to the provider for things like querying VSphere
        # for datacenters before that custom cloud is known to juju.
        app.provider.save_form()

        # if it's a new MAAS or VSphere cloud, save it now that
        # we have a credential
        if app.provider.cloud_type in ['maas', 'vsphere']:
            try:
                juju.get_cloud(app.provider.cloud)
            except LookupError:
                juju.add_cloud(app.provider.cloud,
                               app.provider.cloud_config())

        # This should return the credential name so juju bootstrap knows
        # which credential to bootstrap with
        self.finish()


_controller_class = CredentialsController
