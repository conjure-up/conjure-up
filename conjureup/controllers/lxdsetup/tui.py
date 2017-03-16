import sys

from conjureup import utils


class LXDSetupController:

    def render(self, msg):
        utils.info("")
        utils.info(msg)
        utils.info("")
        sys.exit(1)


_controller_class = LXDSetupController
