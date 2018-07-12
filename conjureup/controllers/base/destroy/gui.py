from conjureup import juju
from conjureup.app_config import app
from conjureup.ui.views.destroy import DestroyView


class Destroy:

    def __init__(self):
        self.view = None

    def finish(self, selection):
        # return controllers.use('destroyconfirm').render(controller, model)
        print(selection)

    def render(self, show_snaps=False):
        models_map = {}
        existing_controllers = juju.get_controllers()['controllers']
        for cname, d in existing_controllers.items():
            models_map[cname] = juju.get_models(cname)
        self.view = DestroyView(app,
                                models=models_map,
                                show_snaps=show_snaps,
                                cb=self.finish)
        self.view.show()


_controller_class = Destroy
