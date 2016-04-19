from conjure.ui.views.deploy_summary import DeploySummaryView
from conjure.utils import pollinate


class DeploySummaryController:
    def __init__(self, app):
        self.app = app

    def finish(self, back=False):
        """ Does the actual deployment and loads the summary controller

        Arguments:
        back: If true will go back to previous controller
        """
        if back:
            return self.app.controllers['deploy'].render(
                self.app.current_model
            )
        else:
            self.app.save()
            self.app.controllers['finish'].render(self.bundle)

    def render(self, bundle):
        self.bundle = bundle
        self.excerpt = ("Please review the deployment summary before "
                        "proceeding.")
        self.view = DeploySummaryView(self.app,
                                      self.bundle,
                                      self.finish)

        self.app.ui.set_header(
            title="Deploy Summary",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
        pollinate(self.app.session_id, 'SS', self.app.log)
