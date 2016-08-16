from conjureup import utils
import sys


class LXDSetupController:
    def render(self):
        utils.info("")
        utils.info("Unable to find a LXD bridge, please run `lxd init` "
                   "and then re-run conjure-up.")
        utils.info("")
        sys.exit(1)

_controller_class = LXDSetupController
