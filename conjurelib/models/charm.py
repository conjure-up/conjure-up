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

import yaml
from tempfile import NamedTemporaryFile


class CharmModel:
    def __init__(self, name, charm_config):
        """ init

        Arguments:
        name: name of charm
        charm_config: Config options from charmstore
        """
        self.name = name
        self.charm_config = {}

    def __getitem__(self, val):
        return self.charm_config.get(val, False)

    def __setitem__(self, key, val):
        self.charm_config[key] = val

    def to_yaml_f(self):
        """ Writes YAML output to a file suitable for passing to Juju during
        deployment

        Returns:
        Path to temporary file
        """
        final = {}
        final[self.name] = self.charm_config
        with NamedTemporaryFile(mode='w+', encoding='utf-8') as tempf:
            tempf.write(yaml.dump(final, default_flow_style=False))
            return tempf.name
