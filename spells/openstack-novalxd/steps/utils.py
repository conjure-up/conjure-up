from subprocess import run, PIPE
from writer import log  # noqa


def slurp(path):
    """ Reads data from path
    :param str path: path of file
    """
    try:
        with open(path) as f:
            return f.read().strip()
    except IOError:
        raise IOError


def parse_openstack_creds(creds_file):
    """ Parses openstack-{admin,ubuntu}-rc for openstack
    credentials

    Arguments:
    creds_file: path to openstack novarc file
    """

    def sanitize_quotes(key):
        if key[0] == key[-1] and key[0] in ("'", '"'):
            return key[1:-1]
        else:
            return key

    cmd = ['bash', '-c', 'source {} && env'.format(creds_file)]
    ret = run(cmd, stdout=PIPE)
    cred_map = {}
    for k in ret.stdout.decode().split("\n"):
        try:
            first, rest = k.split("=")
            cred_map[first] = sanitize_quotes(rest)
        except ValueError:
            log.debug("Skipping {}".format(k))
    return cred_map
