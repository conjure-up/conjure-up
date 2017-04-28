import sys

from conjureup import utils


class LXDSetupController:

    def render(self):
        print("")
        utils.error("Unable to setup LXD networking for deployment")
        print("")
        sys.exit(1)


_controller_class = LXDSetupController
