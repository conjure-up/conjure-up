#!/usr/bin/env python

from ubuntui.utils import Color
from ubuntui.widgets.buttons import menu_btn
from urwid import Text

from base import MockupView


class TestView(MockupView):
    title = 'Add-Ons'
    subtitle = ('Would you like to deploy any additional '
                'workloads to your Canonical Kubernetes deployment?')

    def build_widget(self):
        return [
            Color.body(menu_btn(label='Deis'),
                       focus_map='menu_button focus'),
            Color.body(menu_btn(label='Galactic Fog'),
                       focus_map='menu_button focus'),
            Color.body(menu_btn(label='Rancher'),
                       focus_map='menu_button focus'),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text(''),
            Text('Adds Deis Workflow, and provides the simplest, most '
                 'flexible way for your developers and ops to deploy '
                 'and manage apps - wherever you run them.'),
        ]

    def build_buttons(self):
        return [self.button('SKIP', None)]


if __name__ == '__main__':
    TestView().show()
