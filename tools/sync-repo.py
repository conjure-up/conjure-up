#!/usr/bin/env python3
#
# Sync's upstream git repositories into project directory.

import json
import os
import subprocess
import argparse
import sys
import tempfile
import shutil
import glob
from contextlib import contextmanager


@contextmanager
def chdir(directory):
    """Change the current working directory to a different directory for a code
    block and return the previous directory after the block exits. Useful to
    run commands from a specificed directory.

    :param str directory: The directory path to change to for this context.
    """
    cur = os.getcwd()
    try:
        yield os.chdir(directory)
    finally:
        os.chdir(cur)


def parse_options(argv):
    parser = argparse.ArgumentParser(description="sync-repo",
                                     prog="sync-repo")
    parser.add_argument('-m', '--manifest', dest='manifest_path',
                        metavar='manifest',
                        help='Path to repo manifest')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force syncing, this removes any existing '
                        'directories affected.')
    return parser.parse_args(argv)


def read_manifest(src):
    if not os.path.isfile(src):
        raise Exception("Unable to locate {}".format(src))
    with open(src) as fp:
        return json.load(fp)


def globdirs(src):
    for d in glob.iglob(src, recursive=True):
        if os.path.isdir(d):
            print("Found directory: {}".format(d))
            yield d


def copy_dirs(dirs, src, dst, force=False):
    with chdir(src):
        for d in glob.iglob(dirs):
            dst = os.path.join(dst, d)
            print("Syncing {} to {}".format(d, dst))
            if os.path.isdir(dst) and not force:
                raise Exception(
                    "{} exists, use --force to overwrite.".format(
                        dst))
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.copytree(d, dst)


def git_clone(src, dst):
    print("Cloning: {} to {}".format(src, dst))
    subprocess.check_call(
        'git clone -q {} {}'.format(src, dst), shell=True)


def git_checkout(src, version):
    with chdir(src):
        subprocess.check_call(
            'git checkout -q {}'.format(version), shell=True)


def main():
    opts = parse_options(sys.argv[1:])
    manifest = read_manifest(opts.manifest_path)
    for repo in manifest['repos']:
        with tempfile.TemporaryDirectory() as repo_tmp:
            git_clone(repo['url'], repo_tmp)
            git_checkout(repo_tmp, repo['version'])
            copy_dirs(repo['directories'],
                      repo_tmp,
                      os.path.abspath(os.curdir),
                      opts.force)


if __name__ == "__main__":
    main()
