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


class ProviderModel:

    name = None
    type = None
    env = {}
    config = {}

    # List of available providers
    available = [
        ('Local', 'Deploy to the current machine using containers.'),
        ('MAAS', 'Deploy to a MAAS environment.'),
        ('OpenStack', 'Deploy to an OpenStack environment.')
    ]

    @classmethod
    def to_yaml(cls):
        """ Outputs environment credentials to YAML
        """
        cls.env['default'] = cls.name
        cls.env['environments'] = {
            cls.name: {
                'type': cls.type
            }
        }

        sanitize_config = {k: v for k, v in cls.config.items()
                           if v is not None}
        cls.env['environments'][cls.name].update(sanitize_config)
        return yaml.safe_dump(cls.env, default_flow_style=False)
