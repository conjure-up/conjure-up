import sys

from conjureup import utils


class LXDSetupController:

    def render(self, msg):
        print("")
        utils.info(msg)
        print("")
        sys.exit(1)


_controller_class = LXDSetupController
