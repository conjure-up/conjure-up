""" Snap utilities
"""
from conjureup.utils import run_script
import yaml


def is_installed(snap):
    """ Returns if a snap is installed
    """
    cmd = run_script("snap info {}".format(snap))
    if cmd.returncode == 0:
        out = yaml.load(cmd.stdout.decode())
        if 'installed' in out.keys():
            return True
    return False
