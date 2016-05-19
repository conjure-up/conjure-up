from subprocess import run, CalledProcessError
import tempfile
from conjure.app_config import app


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

    This also gives us the type of the endpoint so we can make further
    descisions. For example, pulling zip's from the charmstore does not
    put all the files inside a top level directory so there is no need
    to run bsdtar with the directory replacement.

    Those types are as follows:
    direct: zip on a webserver somewhere
    vcs: in github or bitbucket (these archives do the same thing with
                                 toplevel directory)
    charmstore: bundle from the jujucharms.com

    Returns:
    The type and url if exists otherwise None.
    """
    if path.startswith("http") and path.endswith(".zip"):
        if remote_exists(path):
            # Path is a full URL to an archived zip
            return ('direct', path)

    if path.startswith("~"):
        namespace, bundle = path.split("/")
        url = ("https://api.jujucharms.com/charmstore/v5"
               "/{}/bundle/{}/archive".format(namespace, bundle))
        return ('charmstore', url)

    remotes = [
        ('vcs', "https://github.com/{}/archive/master.zip".format(path)),
        ('vcs', "https://bitbucket.org/{}/get/master.zip".format(path)),
        ('charmstore',
         "https://api.jujucharms.com/charmstore/v5/{}/archive".format(path)),
    ]
    for r in remotes:
        endpoint_type, url = r
        if remote_exists(url):
            return r
    return None
