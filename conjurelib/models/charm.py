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


class CharmModelException(Exception):
    """ Exception in CharmModel """


class CharmModel:
    """ Stores charm/bundle location for juju deploy
    """
    bundle = {
        "key": None,
        "name": None,
        "summary": None,
        "revision": None
    }

    # Bypass revision from config and pull down latest bundle from charmstore.
    use_latest = False

    @classmethod
    def key(cls):
        """ Returns key of resource
        """
        return cls.bundle.get('key', None)

    @classmethod
    def name(cls):
        """ Returns name of resource
        """
        return cls.bundle.get('name', None)

    @classmethod
    def summary(cls):
        """ Returns summary of resource
        """
        return cls.bundle.get('summary', None)

    @classmethod
    def revision(cls):
        """ Returns revision of resource
        """
        return cls.bundle.get('revision', None)

    @classmethod
    def to_path(cls):
        """ Returns proper path to pass to juju deploy depending
        on if it's a bundle or a charm
        """
        if cls.key() is None or (cls.revision() is
                                 None and not cls.use_latest):
            raise CharmModelException("Unable to determine bundle path.")
        if cls.use_latest:
            return "cs:bundle/{}".format(cls.key())
        else:
            return "cs:bundle/{}/{}".format(cls.key(), cls.revision())
