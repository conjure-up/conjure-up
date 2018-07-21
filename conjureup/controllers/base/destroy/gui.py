from conjureup import errors, snap
from conjureup.models.provider import load_schema
from conjureup.app_config import app
from conjureup.ui.views.destroy import DestroyView
from conjureup.controllers.base.destroyconfirm import gui


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
        return gui.DestroyConfirm().render(selection)

    def render(self):
        show_snaps = False
        if snap.is_installed('microk8s'):
            show_snaps = True

        self.view = DestroyView(app,
                                show_snaps=show_snaps,
                                cb=self.finish)
        self.view.show()


_controller_class = Destroy
