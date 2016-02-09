from conjure.ui.views import MaasJujuModelView
from conjure.models.models import MaasJujuModel
from conjure.controllers.deploy import DeployController


class MaasJujuModelController:
    def __init__(self, common):
        self.common = common
        self.view = MaasJujuModelView(self.common,
                                      self.finish)
        self.model = MaasJujuModel

    def finish(self, result):
        """ Deploys to the maas model
        """
        self.model.config.update({k: v.value for k, v in result.items()})
        DeployController(self.common, self.model).render()

    def render(self):
        self.common['ui'].set_header(
            title="MAAS Juju Model",
            excerpt="Enter your MAAS credentials to "
            "enable deploying to this model."
        )
        self.common['ui'].set_body(self.view)
