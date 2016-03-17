from conjure.ui.views.deploy_summary import DeploySummaryView
# from conjure.controllers.welcome import WelcomeController
from conjure.controllers.finish import FinishController
from conjure.juju import Juju
from functools import partial
from conjure.async import AsyncPool

import q  # noqa


class DeploySummaryController:
    def __init__(self, common, bundle):
        self.common = common
        self.bundle = bundle
        self.excerpt = ("Please review the deployment summary before "
                        "proceeding.")
        self.view = DeploySummaryView(self.common,
                                      self.bundle,
                                      self.finish)

    def finish(self, reset=False):
        """ Load the finish controller or optionally startover.

        Arguments:
        reset: If true will send user back to welcome controller
        """
        if reset:
            # WelcomeController(self.common).render()
            q("reset")
        else:
            AsyncPool.submit(
                partial(Juju.deploy_bundle, self.bundle)
            )
            FinishController(self.common).render()

    def render(self):
        self.common['ui'].set_header(
            title="Deploy Summary",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
