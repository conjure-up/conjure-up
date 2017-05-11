from conjureup import events, utils


class LXDSetupController:

    def render(self):
        print("")
        utils.error("Unable to setup LXD networking for deployment")
        print("")
        events.Shutdown.set(1)


_controller_class = LXDSetupController
