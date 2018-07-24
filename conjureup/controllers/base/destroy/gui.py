from conjureup import errors, controllers
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
        self.view = DestroyView(app,
                                cb=self.finish)
        self.view.show()


_controller_class = Destroy
