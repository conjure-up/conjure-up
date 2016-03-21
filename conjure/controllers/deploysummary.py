from conjure.ui.views.deploy_summary import DeploySummaryView
from conjure.juju import Juju
from functools import partial
from conjure.async import AsyncPool


class DeploySummaryController:
    def __init__(self, app, bundle):
        self.app = app
        self.bundle = bundle
        self.excerpt = ("Please review the deployment summary before "
                        "proceeding.")
        self.view = DeploySummaryView(self.app,
                                      self.bundle,
                                      self.finish)

    def finish(self, reset=False):
        """ Load the finish controller or optionally startover.

        Arguments:
        reset: If true will send user back to welcome controller
        """
        if reset:
            self.app.controllers['welcome'](self.app).render()
        else:
            AsyncPool.submit(
                partial(Juju.deploy_bundle, self.bundle)
            )
            self.app.controllers['finish'](self.app).render()

    def render(self):
        self.app.ui.set_header(
            title="Deploy Summary",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
