from subprocess import run, CalledProcessError
import tempfile
import os
from conjure.app_config import app


def fetcher(spell):
    """ Returns endpoint type

    Arguments:
    spell: full spell indentifier

    Types:
    charmstore-direct: Pulling a single bundle from cs
    charmstore: Querying a keyword/tag in charmstore
    direct: Pulling from a remote webserver
    vcs: Pulling from a remote Vcs like github
    deb: This spell was accessed from one of our official deb packages

    Returns:
    Endpoint type
    """
    if spell.startswith('~'):
        return "charmstore-direct"
    if "/" in spell:
        return "vcs"
    if spell.startswith('http'):
        return "direct"
    return "charmstore"


def remote_exists(path):
    """ Verifies remote url archive exists
    """
    try:
        run('wget --spider -q {}'.format(path), shell=True,
            check=True)
    except CalledProcessError:
        return False
    return True


def download(src, dst, purge_top_level=True):
    """ Download and extract archive

    Arguments:
    src: path to archive
    dst: directory to change to before extract, this directory must already
         exist.
    purge_top_level: purge the toplevel directory and shift all contents up
                     during unzip.
    """
    try:
        if not os.path.isdir(dst):
            os.makedirs(dst)
        with tempfile.TemporaryDirectory() as tmpdirname:
            run("wget -qO {}/temp.zip {}".format(tmpdirname, src),
                shell=True,
                check=True)
            bsdtar_cmd = "bsdtar -xf {}/temp.zip ".format(tmpdirname)
            if purge_top_level:
                bsdtar_cmd += "-s'|[^/]*/||' "
            bsdtar_cmd += "-C {}".format(dst)
            app.log.debug("Extracting spell: {}".format(bsdtar_cmd))
            run(bsdtar_cmd, shell=True, check=True)
    except CalledProcessError as e:
        raise Exception("Unable to download {}: {}".format(src, e))


def get_remote_url(path):
    """ Cycles through known locations to autodetect where to download
    spells from

    Arguments:
    path: Can be local zip, remote zip, or a short url to check
    github, bitbucket, and the charmstore.

    For example, using the charmstore bundle key 'apache-core-batch-processing'
    will check the charmstore and download that bundle.

    Using something like 'ubuntu-solutions-engineering/kubernetes' will check
    GitHub for that spell and download appropriately.

    Returns:
    The url if exists otherwise None.
    """
    if path.startswith("http") and path.endswith(".zip"):
        if remote_exists(path):
            # Path is a full URL to an archived zip
            return path

    if path.startswith("~"):
        namespace, bundle = path.split("/")
        url = ("https://api.jujucharms.com/charmstore/v5"
               "/{}/bundle/{}/archive".format(namespace, bundle))
        return url

    remotes = [
        "https://github.com/{}/archive/master.zip".format(path),
        "https://bitbucket.org/{}/get/master.zip".format(path),
        "https://api.jujucharms.com/charmstore/v5/{}/archive".format(path),
    ]
    for r in remotes:
        if remote_exists(r):
            return r
    return None
