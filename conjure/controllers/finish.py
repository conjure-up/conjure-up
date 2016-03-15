from conjure.ui.views.services import ServicesView
from ubuntui.ev import EventLoop


class FinishController:

    def __init__(self, common):
        self.common = common
        self.view = ServicesView(self.common)

    def refresh(self, *args):
        self.view.refresh_nodes()
        EventLoop.set_alarm_in(1, self.refresh)

    def render(self):
        self.common['ui'].set_header(
            title="Status: {}".format(
                self.common['config']['summary'])
        )
        self.common['ui'].set_body(self.view)

        self.common['ui'].set_footer("Please visit "
                                     "https://jujucharms.com/docs/stable/"
                                     "juju-managing to learn how to manage "
                                     "your new {} solution!".format(
                                         self.common['config']['name']))
        EventLoop.set_alarm_in(1, self.refresh)
