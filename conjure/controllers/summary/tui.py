from . import common
from conjure import utils
import sys


def finish():
    sys.exit(0)


def render(results):
    common.write_results(results)
    utils.info("\n".join(results))
    finish()
