from conjureup.ui.views.lxdsetup import LXDSetupView
from conjureup import utils
from conjureup import controllers
from conjureup.app_config import app
from subprocess import run
from tempfile import NamedTemporaryFile
from ubuntui.ev import EventLoop


class LXDSetupController:
    def __init__(self):
        self.view = None

    def __format_input(self, network):
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

    def __format_conf(self, network):
        """ Formats the lxd bridge config for writing to file
        """
        lines = []
        for k in network.keys():
            lines.append("{}={}".format(k, network[k]))
        return "\n".join(lines)

    def finish(self, needs_lxd_setup=False, lxdnetwork=None, back=False):
        """ Processes the new LXD setup and loads the controller to
        finish bootstrapping the model.

        Arguments:
        back: if true loads previous controller
        needs_lxd_setup: if true prompt user to run lxd init
        """
        if back:
            return controllers.use('clouds').render()

        if needs_lxd_setup:
            EventLoop.remove_alarms()
            EventLoop.exit(1)

        if lxdnetwork is None:
            return app.ui.show_exception_message(
                Exception("Unable to configure LXD network bridge."))

        formatted_network = self.__format_input(lxdnetwork)
        app.log.debug("LXD Config {}".format(formatted_network))

        out = self.__format_conf(formatted_network)

        with NamedTemporaryFile(mode="w", encoding="utf-8",
                                delete=False) as tempf:
            app.log.debug("Saving LXD config to {}".format(tempf.name))
            utils.spew(tempf.name, out)
            sh = run('sudo mv {} /etc/default/lxd-bridge'.format(
                tempf.name), shell=True)
            if sh.returncode > 0:
                return app.ui.show_exception_message(
                    Exception("Problem saving config: {}".format(
                        sh.stderr.decode('utf8'))))

        app.log.debug("Restarting lxd-bridge")
        run("sudo systemctl restart lxd-bridge.service", shell=True)

        utils.pollinate(app.session_id, 'L002')
        controllers.use('newcloud').render(
            cloud='localhost', bootstrap=True)

    def render(self):
        """ Render
        """
        utils.pollinate(app.session_id, 'L001')
        self.view = LXDSetupView(app,
                                 self.finish)

        app.ui.set_header(
            title="Setup LXD Bridge",
        )
        app.ui.set_body(self.view)


_controller_class = LXDSetupController
