from conjure.ui.views.services import ServicesView
from ubuntui.ev import EventLoop


class FinishController:

    def __init__(self, app):
        self.app = app

    def refresh(self, *args):
        self.view.refresh_nodes()
        EventLoop.set_alarm_in(1, self.refresh)

    def render(self):
        self.view = ServicesView(self.app)

        self.app.ui.set_header(
            title="Status: {}".format(
                self.app.config['summary'])
        )
        self.app.ui.set_body(self.view)
        self.app.ui.set_subheader('Deploy Status - (Q)uit')

        self.app.ui.set_footer("Please visit "
                               "https://jujucharms.com/docs/stable/"
                               "juju-managing to learn how to manage "
                               "your new {} solution!".format(
                                   self.app.config['name']))
        EventLoop.set_alarm_in(1, self.refresh)
