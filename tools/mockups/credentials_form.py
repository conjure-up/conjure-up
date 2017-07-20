#!/usr/bin/env python3

from ubuntui.widgets.input import (
    PasswordEditor,
    SelectorHorizontal,
    StringEditor
)

from base import MockupView
from conjureup.models.provider import BaseProvider, Field
from conjureup.ui.views.base import SchemaFormView


class VSphere(BaseProvider):
    AUTH_TYPE = 'userpass'

    def __init__(self):
        self.endpoint = Field(
            label='api endpoint',
            widget=StringEditor(),
            key='endpoint',
            storable=False
        )
        self.user = Field(
            label='user',
            widget=StringEditor(),
            key='user'
        )
        self.password = Field(
            label='password',
            widget=PasswordEditor(),
            key='password'
        )
        self.external_network = Field(
            label='external network',
            widget=SelectorHorizontal([
                '10.0.0.1/24',
                '172.16.0.1/24']),
            key='external-network',
            storable=False
        )
        self.internal_network = Field(
            label='internal network',
            widget=SelectorHorizontal([
                '10.10.1.1/24',
                '172.18.1.1/24']),
            key='internal-network',
            storable=False
        )
        self.datasource = Field(
            label='datasource',
            widget=SelectorHorizontal([
                'VMStorage1',
                'VMStorage2',
                'VMStorage3']),
            key='datasource',
            storable=False
        )

    def fields(self):
        return [
            self.endpoint,
            self.user,
            self.password,
            self.external_network,
            self.internal_network,
            self.datasource
        ]


class TestView(MockupView, SchemaFormView):
    title = "Credential Creation"
    subtitle = "New Credential Setup"

    def __init__(self, *args, **kwargs):
        self.header = "Enter your VSphere credentials"
        self.schema = VSphere()
        super().__init__(self.schema, None, *args, **kwargs)


if __name__ == '__main__':
    TestView().show()
