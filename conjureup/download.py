from subprocess import run, CalledProcessError
import shutil
import os
from conjureup.consts import UNSPECIFIED_SPELL
from conjureup.app_config import app
import requests
from progressbar import (ProgressBar, Bar,
                         Percentage, AnimatedMarker,
                         UnknownLength)

from enum import Enum


class EndpointType(Enum):
    LOCAL_DIR = 0               # A path on the local filesystem
    LOCAL_SEARCH = 1            # A spell or keyword to up in the index
    VCS = 2                     # A remote VCS url (git, bzr)
    HTTP = 3                    # An http/s URL


def detect_endpoint(spell):
    """ Returns endpoint type for fetching the spell

    Arguments:
    spell: full spell indentifier

    Returns
    EndpointType or None, if no spell was specified
    """
    if os.path.isdir(spell) or spell == '.':
        return EndpointType.LOCAL_DIR
    if spell.startswith('http'):
        return EndpointType.HTTP
    if "/" in spell:
        return EndpointType.VCS
    if spell == UNSPECIFIED_SPELL:
        return None

    return EndpointType.LOCAL_SEARCH


def remote_exists(path):
    """ Verifies remote url archive exists
    """
    return requests.head(path).ok


def download_local(src, dst):
    """ Copies spell from local filesystem into cache
    """
    try:
        shutil.rmtree(dst, ignore_errors=True)
        app.log.debug("Path is local filesystem, copying {} to {}".format(
            src, dst))
        shutil.copytree(src, dst)
        return
    except Exception as e:
        app.log.debug("Failed to download local spell: {}".format(e))
        raise e


def download_requests_stream(request_stream, destination, message=None):
    """ This is a facility to download a request with nice progress bars.
    """
    if not message:
        message = 'Downloading {!r}'.format(os.path.basename(destination))

    total_length = int(request_stream.headers.get('Content-Length', '0'))
    if total_length:
        progress_bar = ProgressBar(
            widgets=[message,
                     Bar(marker='=', left='[', right=']'),
                     ' ', Percentage()],
            maxval=total_length)
    else:
        progress_bar = ProgressBar(
            widgets=[message, AnimatedMarker()],
            maxval=UnknownLength)

    total_read = 0
    progress_bar.start()
    with open(destination, 'wb') as destination_file:
        for buf in request_stream.iter_content(1024):
            destination_file.write(buf)
            total_read += len(buf)
            progress_bar.update(total_read)
    progress_bar.finish()


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
        shutil.rmtree(dst, ignore_errors=True)
        os.makedirs(dst)
        request = requests.get(src, stream=True)
        tmpfile = os.path.join(os.environ.get('TEMPDIR', '/tmp'),
                               'temp.zip')
        download_requests_stream(request, tmpfile)
        bsdtar_cmd = "bsdtar -xf {} ".format(tmpfile)
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
    path: Can be local, local zip, remote zip, or a short url to check
    github, bitbucket, etc.

    Using something like 'ubuntu-solutions-engineering/kubernetes' will check
    GitHub for that spell and download appropriately.

    Returns:
    The url if exists otherwise None.
    """

    if path.startswith("http") and path.endswith(".zip"):
        if remote_exists(path):
            # Path is a full URL to an archived zip
            return path

    remotes = [
        "https://github.com/{}/archive/master.zip".format(path),
        "https://bitbucket.org/{}/get/master.zip".format(path)
    ]
    for r in remotes:
        app.log.debug("Checking remote URL: {}".format(r))
        if remote_exists(r):
            return r
    return None
