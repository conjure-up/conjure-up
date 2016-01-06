# Copyright (c) 2015 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import shutil
import os


class UtilsException(Exception):
    """ Error in utils
    """
    pass


class Host:
    """ host utilities
    """

    @classmethod
    def install_user(cls):
        """ returns sudo user
        """
        user = os.getenv('SUDO_USER', None)
        if not user:
            user = os.getenv('USER', 'root')
        return user

    @classmethod
    def install_home(cls):
        """ returns installer user home
        """
        return os.path.expanduser("~" + cls.install_user())


class FS:
    """ filesystem utility class
    """

    @classmethod
    def chown(cls, path, user, group=None, recursive=False):
        """ Change user/group ownership of file

        Arguments:
        path: path of file or directory
        user: new owner username
        group: new owner group name
        recursive: set files/dirs recursively
        """
        try:
            if not recursive or os.path.isfile(path):
                shutil.chown(path, user, group)
            else:
                for root, dirs, files in os.walk(path):
                    shutil.chown(root, user, group)
                    for item in dirs:
                        shutil.chown(os.path.join(root, item), user, group)
                    for item in files:
                        shutil.chown(os.path.join(root, item), user, group)
        except OSError as e:
            raise UtilsException(e)

    @classmethod
    def spew(cls, path, data, owner=None):
        """ Writes data to path
        Arguments:
        path: path of file to write to
        data: contents to write
        owner: optional owner of file
        """
        with open(path, 'w') as f:
            f.write(data)
        if owner:
            try:
                cls.chown(path, owner)
            except:
                raise UtilsException(
                    "Unable to set ownership of {}".format(path))

    @classmethod
    def slurp(cls, path):
        """ Reads data from path

        Arguments:
        path: path of file
        """
        try:
            with open(path) as f:
                return f.read().strip()
        except IOError:
            raise IOError
