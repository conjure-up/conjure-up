from conjure.ui.views.local import LocalJujuModelView
from conjure.models.jujumodels.local import LocalJujuModel
from conjure.juju import Juju
from conjure.controllers.deploy import DeployController


class LocalJujuModelController:
    def __init__(self, common):
        self.common = common
        self.view = LocalJujuModelView(self.common,
                                       self.finish)
        self.model = LocalJujuModel

    def finish(self, result):
        """ Deploys to the local model
        """
        self.model.config.update({k: v.value for k, v in result.items()})
        Juju.create_environment()
        DeployController(self.common, self.model).render()

    def render(self):
        self.common['ui'].set_header(
            title="Local Model",
            excerpt="Enter optional configuration items for the Juju Local "
            "model before deploying."
        )
        self.common['ui'].set_body(self.view)
