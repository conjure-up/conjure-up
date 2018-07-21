from conjureup import errors, snap, controllers
from conjureup.models.provider import load_schema
from conjureup.app_config import app
from conjureup.ui.views.destroy import DestroyView


class Destroy:

    def __init__(self):
        self.view = None

    def finish(self, selection):
        if selection['type'] == 'juju':
            app.provider = load_schema(selection['cloud'])
            try:
                app.provider.load(selection['cloud'])
            except errors.SchemaCloudError as e:
                raise e
        return controllers.use('destroyconfirm').render(selection)

    def render(self):
        # TODO: Get a list of spells with a spell-type: snap,
        # and if installed, list them here.
        show_snaps = False
        if snap.is_installed('microk8s'):
            show_snaps = True

        self.view = DestroyView(app,
                                show_snaps=show_snaps,
                                cb=self.finish)
        self.view.show()


_controller_class = Destroy
