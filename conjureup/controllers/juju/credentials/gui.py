from os import path

import yaml

from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.consts import CUSTOM_PROVIDERS, cloud_types
from conjureup.ui.views.credentials import (
    CredentialPickerView,
    NewCredentialView
)

from . import common


class CredentialsController(common.BaseCredentialsController):
    def render(self, going_back=False):
        self.load_credentials()
        if app.provider.cloud_type == cloud_types.LOCAL:
            # no credentials required for localhost
            if going_back:
                self.back()
            else:
                self.finish()
        elif len(self.credentials) >= 1:
            self.render_picker()
        elif not app.provider.credential:
            self.render_form()
        else:
            if going_back:
                self.back()
            else:
                self.finish()

    def render_form(self):
        view = NewCredentialView(self.save_credential, self.switch_views)
        view.show()

    def render_picker(self):
        view = CredentialPickerView(self.credentials, app.provider.credential,
                                    self.select_credential, self.back)
        view.show()

    def switch_views(self):
        if self.was_picker:
            self.was_picker = False
            return self.render_picker()
        else:
            self.was_picker = True
            self.render_form()

    def back(self):
        return controllers.use('clouds').render(going_back=True)

    def _format_creds(self):
        """ Formats the credentials into strings from the widgets values
        """
        formatted = {'auth-type': app.provider.auth_type}
        for field in app.provider.form.fields():
            if not field.storable:
                continue
            formatted[field.key] = field.value

        return formatted

    def select_credential(self, credential):
        if credential is None:
            self.switch_views()
        else:
            app.provider.credential = credential
            self.finish()

    def save_credential(self):
        app.loop.create_task(self._save_credential())

    async def _save_credential(self):
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
        await app.provider.save_form()

        # if it's a new MAAS or VSphere cloud, save it now that
        # we have a credential
        if app.provider.cloud_type in CUSTOM_PROVIDERS:
            try:
                juju.get_cloud(app.provider.cloud)
            except LookupError:
                juju.add_cloud(app.provider.cloud,
                               await app.provider.cloud_config())

        # This should return the credential name so juju bootstrap knows
        # which credential to bootstrap with
        self.finish()


_controller_class = CredentialsController
