import os
import sys
import yaml
import argparse
from code import interact


def parse_options(argv):
    parser = argparse.ArgumentParser(description='Macumba Shell',
                                     prog='macumba-shell')
    parser.add_argument('--v1', action='store_true', dest='v1',
                        help='Use Juju 1.x API')
    parser.add_argument('--v2', action='store_true', dest='v2',
                        help='Use Juju 2.x API')
    parser.add_argument('-m', '--model', dest='model',
                        help='The Environment(v1)/Model(v2) to connect to.')
    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])
    if not opts.model:
        raise Exception("Must choose a Environment/Model.")
    if opts.v1:
        juju_home = os.getenv("JUJU_HOME", "~/.juju")
        from .v1 import JujuClient  # noqa
        env = os.path.expanduser(
            os.path.join(
                juju_home,
                "environments/{}.jenv".format(opts.model)))
        if not os.path.isfile(env):
            raise Exception("Unable to locate: {}".format(env))
        env_yaml = yaml.load(open(env))
        uuid = env_yaml['environ-uuid']
        server = env_yaml['state-servers'][0]
        password = env_yaml['password']
        user = env_yaml['user']
        url = os.path.join('wss://', server, 'environment', uuid, 'api')

    elif opts.v2:
        xdg_home = os.getenv("XDG_DATA_HOME", "~/.local/share")
        juju_home = os.path.join(xdg_home, 'juju')
        from .v2 import JujuClient  # noqa
        env = os.path.expanduser(
            os.path.join(
                juju_home,
                "models/cache.yaml"))
        if not os.path.isfile(env):
            raise Exception("Unable to locate: {}".format(env))

        env = yaml.load(open(env))
        uuid = env['server-user'][opts.model]['server-uuid']
        server = env['server-data'][uuid]['api-endpoints'][0]
        password = env['server-data'][uuid]['identities']['admin']
        url = os.path.join('wss://', server, 'model', uuid, 'api')
    else:
        raise Exception("Could not determine Juju API Version to use.")

    print('Connecting to {}'.format(url))
    j = JujuClient(url=url, password=password)
    j.login()

    interact(banner="juju client logged in. Object is named 'j',"
             " so j.status() will fetch current status as a dict.",
             local=locals())
