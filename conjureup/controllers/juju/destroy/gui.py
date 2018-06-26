from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.ui.views.destroy import DestroyView


class Destroy:

    def __init__(self):
        self.view = None

    def finish(self, controller, model):
        return controllers.use('destroyconfirm').render(controller, model)

    def render(self):
        models_map = {}
        existing_controllers = juju.get_controllers()['controllers']
        for cname, d in existing_controllers.items():
            models_map[cname] = juju.get_models(cname)
        self.view = DestroyView(app,
                                models=models_map,
                                cb=self.finish)
        self.view.show()


_controller_class = Destroy
