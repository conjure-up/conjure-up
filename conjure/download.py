from subprocess import run, CalledProcessError
import tempfile


def remote_exists(path):
    """ Verifies remote url archive exists
    """
    try:
        run('wget --spider -q {}'.format(path), shell=True,
            check=True)
    except CalledProcessError:
        return False
    return True


def download(src, dst):
    """ Download and extract archive

    Arguments:
    src: path to archive
    dst: directory to change to before extract, this directory must already
         exist.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            run("wget -qO {}/temp.zip {}".format(tmpdirname, src),
                shell=True,
                check=True)
            run("bsdtar -xf {}/temp.zip -s'|[^/]*/||' -C {}".format(
                tmpdirname, dst), shell=True, check=True)
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
