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

""" sbuild helpers
"""
from .shell import shell
from tornado.process import cpu_count


class SBuildException(Exception):
    """ Problem with sbuild
    """
    pass


class SBuild:
    @classmethod
    def buildpackage(cls, series="trusty"):
        """ Builds a debian package

        Arguments:
        series: Ubuntu series
        """
        if not cls._has_schroot(series):
            raise SBuildException(
                "Unable to find chroot for {}, run create_build_env "
                "to setup a new environment".format(series))
        sh = shell("sbuild -d {}-amd64 -j{}".format(series, cpu_count()))
        if sh.code > 0:
            raise SBuildException("Failed to build: {}".format(sh.errors()))

    @classmethod
    def create_build_env(cls, series="trusty"):
        """ Creates a sbuild environment

        Arguments:
        series: Ubuntu series, defaults to trusty
        """
        sh = shell("mk-sbuild {}".format(series))
        if sh.code > 0:
            raise SBuildException(
                "Could not create build environment: {}".format(sh.errors()))

    @classmethod
    def _has_schroot(cls, series):
        """ Checks if chroot exists for series

        Arguments:
        series: Ubuntu series
        """
        sh = shell("schroot -l")
        if sh.code > 0:
            raise SBuildException(
                "Problem listing chroots: {}".format(sh.errors()))
        series = "chroot:{}-amd64".format(series)
        if series in sh.output():
            return True
        return False
