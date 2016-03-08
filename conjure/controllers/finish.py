from conjure.ui.views.finish import FinishView
from ubuntui.ev import EventLoop


class FinishController:

    def __init__(self, common):
        self.common = common
        self.view = FinishView(self.common, self.finish)

    def finish(self):
        """ handles deployment
        """
        EventLoop.exit(0)

    def render(self):
        self.common['ui'].set_header(
            title="Installing solution: {}".format(
                self.common['config']['summary']),
            excerpt="Please wait while services are being "
            "deployed."
        )
        self.common['ui'].set_body(self.view)

        self.view.set_status("\n\n")
        self.view.set_status("Completed the install, please visit "
                             "https://jujucharms.com/docs/stable/"
                             "juju-managing to learn how to manage "
                             "your new {} solution!".format(
                                 self.common['config']['name']))
