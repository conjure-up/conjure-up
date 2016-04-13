from conjure.ui.views.lxdsetup import LXDSetupView
from conjure.utils import pollinate, spew
from conjure.shell import shell
from tempfile import NamedTemporaryFile


class LXDSetupController:
    """ Renders a LXD bridge configuration view
    """

    def __init__(self, app):
        self.app = app

    def _format_input(self, network):
        """ Formats the network dictionary into strings from the widgets values
        """
        formatted = {}
        for k, v in network.items():
            widget, help_text = v
            if k.startswith('_'):
                # Not a widget but a private key
                k = k[1:]
            if isinstance(widget.value, bool) and widget.value:
                formatted[k] = str("true")
            elif isinstance(widget.value, bool) and not widget.value:
                formatted[k] = str("false")
            elif widget.value is None:
                formatted[k] = str("")
            else:
                formatted[k] = widget.value
        return formatted

    def _format_conf(self, network):
        """ Formats the lxd bridge config for writing to file
        """
        lines = []
        for k in network.keys():
            lines.append("{}={}".format(k, network[k]))
        return "\n".join(lines)

    def finish(self, lxdnetwork=None, back=False):
        """ Processes the new LXD setup and loads the controller to
        finish bootstrapping the model.

        Arguments:
        back: if true loads previous controller
        """
        if back:
            return self.app.controllers['clouds'].render()

        if lxdnetwork is None:
            return self.app.ui.show_exception_message(
                Exception("Unable to configure LXD network bridge."))

        formatted_network = self._format_input(lxdnetwork)
        self.app.log.debug("LXD Config {}".format(formatted_network))

        out = self._format_conf(formatted_network)

        with NamedTemporaryFile(mode="w", encoding="utf-8",
                                delete=False) as tempf:
            self.app.log.debug("Saving LXD config to {}".format(tempf.name))
            spew(tempf.name, out)
            sh = shell('sudo mv {} /etc/default/lxd-bridge'.format(
                tempf.name))
            if sh.code > 0:
                return self.app.ui.show_exception_message(
                    Exception("Problem saving config: {}".format(sh.errors())))

        pollinate(self.app.session_id, 'L002', self.app.log)
        self.app.controllers['jujucontroller'].render(
            cloud='lxd', bootstrap=True)

    def render(self):
        """ Render
        """
        pollinate(self.app.session_id, 'L001', self.app.log)
        self.view = LXDSetupView(self.app,
                                 self.finish)

        self.app.ui.set_header(
            title="Setup LXD Bridge",
        )
        self.app.ui.set_body(self.view)
