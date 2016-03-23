from conjure.ui.views.bootstrapwait import BootstrapWaitView


class BootstrapWaitController:
    def __init__(self, app):
        self.app = app

    def render(self):
        self.view = BootstrapWaitView(self.app)
        self.app.ui.set_header(
            title="Bootstrapping",
            excerpt="Please wait while Juju bootstraps the model.",
        )
        self.app.ui.set_body(self.view)
        self.app.ui.set_subheader("Press (Q) to cancel bootstrap and exit.")
