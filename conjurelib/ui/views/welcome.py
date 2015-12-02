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

from urwid import WidgetWrap, Text, Pile
from ubuntui.widgets.input import (StringEditor,
                                   IntegerEditor,
                                   YesNo)


class WelcomeView(WidgetWrap):
    def __init__(self, common):
        self.common = common
        self.charm_config = self.common['config']['fields']
        self.charm_config_ui = {}
        super().__init__(Pile(self.build_config_items()))

    def _generate_config_options(self):
        """ Generates the charm config map and associating the proper input
        widget for the option type

        The config items are a dictionary of:
        {'config': {'Type': boolean,
                    'Default': False,
                    'Description': "config desc"}}
        """
        for k, v in self.charm_config.items():
            description = Text(k[v]['Description'])
            itype = k[v]['Type']
            if itype == 'string':
                default = StringEditor(default=k[v]['Default'])
            elif itype == 'int':
                default = IntegerEditor(default=k[v]['Default'])
            else:
                default = YesNo()
                # Check the boolean type for setting initial state of
                # radio button
                if k[v]['Default']:
                    default.set_default('Yes', True)

            self.charm_config_ui[k] = {
                'input': default,
                'description': description
            }

    def build_config_items(self):
        """ Builds the form for modifying the charms config options
        """
        return [Text("Nup")]
