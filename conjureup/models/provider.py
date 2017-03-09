from collections import OrderedDict

from ubuntui.widgets.input import PasswordEditor, StringEditor, YesNo

""" Defining the schema

The schema contains attributes for rendering proper credentials for the
different clouds. There are a few cases where additional attributes are
required and some that are required aren't necessarily meant to be edited.

The schema uses a simple single first value for describing the type of
attribute it is. If there is no indicating first character it is considered
public, editable, and viewable by the end user.

The schema contains the following:

- If a key starts with '_' it is private, not editable, but stored in
  the credentials as is.
- If a key starts with '@' it is public, editable, but _not_ stored in
  the credentials file.
- If the key does not start with any sigil it is public, editable, and
  stored in the credentials file.

Examples:

('maas', OrderedDict([
  ('@maas-server', StringEditor()) # Required input not stored.
  ('_auth-type', 'oauth1) # Required, not editable and is stored.
  ('maas-oauth', StringEditor()) # required, editable, and stored.
])
"""
aws = {
    'auth-type': 'access-key',
    'fields': [
        {'label': None,
         'input': StringEditor(),
         'key': 'access-key'},
        {'label': None,
         'input': StringEditor(),
         'key': 'secret-key'}
    ]
}

maas = {
    'auth-type': 'oauth1',
    'fields': [
        {
            'label': None,
            'input': StringEditor(),
            'key': 'maas-server',
            'storable': False
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'maas-oauth'
        }
    ]
}

azure = {
    'auth-type': 'userpass',
    'fields': [
        {
            'label': None,
            'input': StringEditor(),
            'key': 'application-id'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'subscription-id'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'tenant-id'
        },
        {
            'label': None,
            'input': PasswordEditor(),
            'key': 'application-password'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'location'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'endpoint'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'storage-endpoint'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'storage-account-type'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'storage-account'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'storage-account-key'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'controller-resource-group'
        },

    ]
}

google = {
    'auth-type': 'oauth2',
    'fields': [
        {
            'label': None,
            'input': StringEditor(),
            'key': 'private-key'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'client-id'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'client-email'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'region'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'project-id'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'image-endpoint'
        }

    ]
}

cloudsigma = {
    'auth-type': 'userpass',
    'fields': [
        {
            'label': None,
            'input': StringEditor(),
            'key': 'username'
        },
        {
            'label': None,
            'input': PasswordEditor(),
            'key': 'password'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'region'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'endpoint'
        }

    ]
}

joyent = {
    'auth-type': 'access-key',
    'fields': [
        {
            'label': None,
            'input': StringEditor(),
            'key': 'sdc-user'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'sdc-key-id'
        },
        {
            'label': None,
            'input': StringEditor(
                default="https://us-west-1.api.joyentcloud.com"),
            'key': 'sdc-url'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'private-key-path'
        },
        {
            'label': None,
            'input': StringEditor(default='rsa-sha256'),
            'key': 'algorithm'
        }
    ]
}

openstack = {
    'auth-type': 'userpass',
    'fields': [
        {
            'label': None,
            'input': StringEditor(),
            'key': 'username'
        },
        {
            'label': None,
            'input': PasswordEditor(),
            'key': 'password'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'tenant-name'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'auth-url'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'auth-mode'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'access-key'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'secret-key'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'region'
        },
        {
            'label': None,
            'input': YesNo(),
            'key': 'use-floating-ip'
        },
        {
            'label': None,
            'input': YesNo(),
            'key': 'use-default-secgroup'
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'network'
        }
    ]
}

vsphere = {
    'auth-type': 'userpass',
    'fields': [
        {
            'label': 'vcenter api-endpoint',
            'input': StringEditor(),
            'key': 'host'
        },
        {
            'label': 'vcenter user',
            'input': StringEditor(),
            'key': 'user'
        },
        {
            'label': 'vcenter password',
            'input': PasswordEditor(),
            'key': 'password'
        },
        {
            'label': 'datacenter',
            'input': StringEditor(),
            'key': 'regions',
            'storable-as': list()
        },
        {
            'label': None,
            'input': StringEditor(),
            'key': 'external-network'
        },
    ]
}


Schema = [
    ('aws', aws),
    ('aws-china', aws),
    ('aws-gov', aws),
    ('maas', maas),
    ('azure', azure),
    ('azure-china', azure),
    ('google', google),
    ('cloudsigma', cloudsigma),
    ('joyent', joyent),
    ('openstack', openstack),
    ('rackspace', openstack),
    ('vsphere', vsphere)
]


def load_schema(cloud):
    """ Loads a schema
    """
    for s in Schema:
        k, v = s
        if cloud == k:
            return v
    raise Exception("Could not find schema for: {}".format(cloud))


SchemaV1 = OrderedDict([
    ('aws', OrderedDict([
        ('_auth-type', 'access-key'),
        ('access-key', StringEditor()),
        ('secret-key', StringEditor())
    ])),
    ('aws-china', OrderedDict([
        ('_auth-type', 'access-key'),
        ('access-key', StringEditor()),
        ('secret-key', StringEditor())
    ])),
    ('aws-gov', OrderedDict([
        ('_auth-type', 'access-key'),
        ('access-key', StringEditor()),
        ('secret-key', StringEditor())
    ])),
    ('maas', OrderedDict([
        ('_auth-type', 'oauth1'),
        ('@maas-server', StringEditor()),
        ('maas-oauth', StringEditor())
    ])),
    ('azure', OrderedDict([
        ('_auth-type', 'userpass'),
        ('application-id', StringEditor()),
        ('subscription-id', StringEditor()),
        ('tenant-id', StringEditor()),
        ('application-password', PasswordEditor()),
        ('location', StringEditor()),
        ('endpoint', StringEditor()),
        ('storage-endpoint', StringEditor()),
        ('storage-account-type', StringEditor()),
        ('storage-account', StringEditor()),
        ('storage-account-key', StringEditor()),
        ('controller-resource-group', StringEditor())
    ])),
    ('azure-china', OrderedDict([
        ('_auth-type', 'userpass'),
        ('application-id', StringEditor()),
        ('subscription-id', StringEditor()),
        ('tenant-id', StringEditor()),
        ('application-password', PasswordEditor()),
        ('location', StringEditor()),
        ('endpoint', StringEditor()),
        ('storage-endpoint', StringEditor()),
        ('storage-account-type', StringEditor()),
        ('storage-account', StringEditor()),
        ('storage-account-key', StringEditor()),
        ('controller-resource-group', StringEditor())
    ])),
    ('google', OrderedDict([
        ('private-key', StringEditor()),
        ('client-id', StringEditor()),
        ('client-email', StringEditor()),
        ('region', StringEditor()),
        ('project-id', StringEditor()),
        ('image-endpoint', StringEditor())
    ])),
    ('cloudsigma', OrderedDict([
        ('username', StringEditor()),
        ('password', PasswordEditor()),
        ('region', StringEditor()),
        ('endpoint', StringEditor())
    ])),
    ('joyent', OrderedDict([
        ('sdc-user', StringEditor()),
        ('sdc-key-id', StringEditor()),
        ('sdc-url', StringEditor(
            default='https://us-west-1.api.joyentcloud.com')),
        ('private-key-path', StringEditor()),
        ('algorithm', StringEditor(default='rsa-sha256'))
    ])),
    ('openstack', OrderedDict([
        ('_auth-type', 'userpass'),
        ('username', StringEditor()),
        ('password', PasswordEditor()),
        ('tenant-name', StringEditor()),
        ('auth-url', StringEditor()),
        ('auth-mode', StringEditor()),
        ('access-key', StringEditor()),
        ('secret-key', StringEditor()),
        ('region', StringEditor()),
        ('use-floating-ip', YesNo()),
        ('use-default-secgroup', YesNo()),
        ('network', StringEditor())
    ])),
    ('rackspace', OrderedDict([
        ('_auth-type', 'userpass'),
        ('username', StringEditor()),
        ('password', PasswordEditor()),
        ('tenant-name', StringEditor()),
        ('auth-url', StringEditor()),
        ('auth-mode', StringEditor()),
        ('access-key', StringEditor()),
        ('secret-key', StringEditor()),
        ('region', StringEditor()),
        ('use-floating-ip', YesNo()),
        ('use-default-secgroup', YesNo()),
        ('network', StringEditor())
    ])),
    ('vsphere', OrderedDict([
        ('datacenter', StringEditor()),
        ('host', StringEditor()),
        ('user', StringEditor()),
        ('password', PasswordEditor()),
        ('external-network', StringEditor())
    ])),
    ('manual', OrderedDict([
        ('bootstrap-host', StringEditor()),
        ('bootstrap-user', StringEditor()),
        ('use-sshstorage', YesNo())
    ])),
])
