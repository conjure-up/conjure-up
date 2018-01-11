#!/usr/bin/env python

from base import MockupView
from conjureup.app_config import app
from conjureup.models.step import StepModel
from conjureup.ui.views.steps import ShowStepsView
from conjureup.ui.widgets.step import StepForm


class TestView(MockupView, ShowStepsView):
    title = 'Deis Setup'
    subtitle = ('Please provide the information below, which will '
                'be used to configure Deis when it is added.')

    def build_widget(self):
        app.steps_data['name'] = {
            'USERNAME': 'admin',
            'PASSWORD': '',
            'EMAIL': '',
        }
        super().build_widget()
        self.add_step(StepForm(app, StepModel({
            'description': 'Download Deis CLI',
            'viewable': True,
        }, 'filename', 'name', 'source')))
        self.add_step(StepForm(app, StepModel({
            'description': 'Create Admin User',
            'viewable': True,
            'additional-input': [
                {'label': 'Username',
                 'key': 'USERNAME',
                 'type': 'text'},
                {'label': 'Password',
                 'key': 'PASSWORD',
                 'type': 'password'},
                {'label': 'Email',
                 'key': 'EMAIL',
                 'type': 'text'},
            ],
        }, 'filename', 'name', 'source')))
        return self.step_pile


if __name__ == '__main__':
    TestView().show()
