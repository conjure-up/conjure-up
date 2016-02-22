from conjure.ui.views.local import LocalJujuModelView
from conjure.models.jujumodel import JujuModel
from conjure.controllers.deploy import DeployController


class LocalJujuModelController:
    def __init__(self, common):
        self.common = common
        self.view = LocalJujuModelView(self.common,
                                       self.finish)
        self.model = JujuModel(self.common['juju-modles']['name'])
        # If there are no options go directly to finish
        if not self.model['options']:
            self.finish()

    def finish(self, result=None):
        """ Deploys to the local model
        """
        if result is not None:
            self.model.config.update({k: v.value for k, v in result.items()})
        DeployController(self.common, self.model).render()

    def render(self):
        self.common['ui'].set_header(
            title="Local Model",
            excerpt="Enter optional configuration items for the Juju Local "
            "model before deploying."
        )
        self.common['ui'].set_body(self.view)
