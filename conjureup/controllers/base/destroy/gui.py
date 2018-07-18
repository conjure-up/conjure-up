from conjureup import juju, errors
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
            return gui.DestroyConfirm().render(selection['controller'],
                                               selection['model'])

        if selection['type'] == 'snap':
            print("Uninstalling {}".format(selection['snap']))

    def render(self, show_snaps=False):
        deployed_map = {}
        existing_controllers = juju.get_controllers()['controllers']
        for cname, d in existing_controllers.items():
            deployed_map[cname] = {'controller': d}
            deployed_map[cname].update(**juju.get_models(cname))
        self.view = DestroyView(app,
                                deployed_map=deployed_map,
                                show_snaps=show_snaps,
                                cb=self.finish)
        self.view.show()


_controller_class = Destroy
