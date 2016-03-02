""" Project Scaffolding entrypoint
"""

import argparse
import sys
import json
import os
from conjure.shell import shell
from conjure.lxd import LXD


class ScaffoldException(Exception):
    """ Error in scaffolding
    """
    pass


class Scaffold:
    def __init__(self, opts):
        """ init

        Arguments:
        opts: Options passed in from cli
        """
        if os.path.isdir(opts.directory):
            raise ScaffoldException(
                "{} exists, please specify another.".format(opts.directory)
            )

        shell('mkdir -p {}'.format(opts.directory))

        config_path = "/usr/share/{}/config.json".format(opts.name)
        if not os.path.isfile(config_path):
            raise ScaffoldException(
                "Unable to find configuration file {}".format(config_path)
            )
        with open(config_path) as configfp:
            config = json.load(configfp)

        for bundle in config['bundles']:
            bundle_key_path = os.path.join(opts.directory, bundle['key'])
            print("Creating {} directory".format(bundle_key_path))
            shell('mkdir -p {}'.format(bundle_key_path))

        LXD.render_lxd_sh(os.path.join(opts.directory, 'lxd.sh'))


def parse_options(argv):
    parser = argparse.ArgumentParser(description="Conjure scaffold",
                                     prog="conjure-scaffold")
    parser.add_argument('-n', '--name', dest='name', metavar='package_name',
                        help='Name of package')
    parser.add_argument('directory',
                        help='directory to scaffold the project in')

    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])

    if not opts.name:
        raise ScaffoldException(
            "A package name is required.")

    if not opts.directory:
        raise ScaffoldException(
            "A project directory is required."
        )

    try:
        Scaffold(opts)
        sys.exit(0)
    except ScaffoldException as e:
        print(e)
        sys.exit(1)
