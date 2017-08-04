import ipaddress
from collections import OrderedDict
from functools import partial
from subprocess import CalledProcessError
from urllib.parse import urljoin, urlparse

from ubuntui.widgets.input import (
    PasswordEditor,
    SelectorHorizontal,
    StringEditor,
    YesNo
)
from urwid import Text

from conjureup.app_config import app
from conjureup.juju import get_cloud
from conjureup.models.credential import CredentialManager
from conjureup.utils import (
    arun,
    get_physical_network_interfaces,
    is_valid_hostname
)
from conjureup.vsphere import VSphereClient, VSphereInvalidLogin


""" Defining the schema

The schema contains attributes for rendering proper credentials.

A typical schema is:

'auth-type': 'access-key' - defines the auth type supported by provider
'login':     - If subsequent views require specific provider
               information, make sure to log into those relevant apis
'fields': [] - editable fields in the ui, each field can contain:
  'label'    - Friendly label to the user
  'widget'   - Input widget
  'key'      - key that matches what the provider expects for authentication
  'storable' - if False will skip storing key=value in credentials
  'validator'- Function to check validity, returns (Boolean, "Optional error")
"""


class Field:
    """ Field class with validation
    """

    def __init__(self,
                 label=None,
                 widget=None,
                 key=None,
                 storable=True,
                 error=None,
                 required=True,
                 validator=None):
        self.label = label
        self.widget = widget
        self.key = key
        self.storable = storable
        self.error = Text("")
        self.required = required
        self.validator = validator

    def validate(self):
        """ Validator for field
        """
        self.error.set_text("")

        if self.required and not self.value:
            self.error.set_text("This field is required and cannot be empty.")
            return False
        if self.validator and callable(self.validator):
            is_valid, msg = self.validator()
            if not is_valid:
                self.error.set_text(msg)
                return False
        return True

    @property
    def value(self):
        return self.widget.value

    @value.setter  # NOQA
    def value(self, value):
        self.widget.value = value


class Form:
    """ Form containing widget fields
    """

    def __init__(self, widgets):
        self._fields = []
        for w in widgets:
            key = w.key.replace('-', '_')
            setattr(self, key, w)
            self._fields.append(getattr(self, key))

    def fields(self):
        return self._fields


class BaseProvider:
    """ Base provider for all schemas
    """

    def __init__(self):
        # Supported cloud authentication type
        self.auth_type = None

        # Juju cloud endpoint
        self.endpoint = None

        # Current Juju model selected
        self.model = None

        # Juju model defaults
        self.model_defaults = None

        # Current Juju controller selected
        self.controller = None

        # Current Juju cloud selected
        self.cloud = None

        # Current Juju cloud type selected
        self.cloud_type = None

        # Juju cloud regions
        self.regions = []

        # Current selected Juju cloud region
        self.region = None

        # Current credential
        self.credential = None

        # Attached api client
        self.client = None

        # Is this provider authenticated for api calls to itself?
        self.authenticated = False

        # Input form associated with provider
        self.form = None

    def is_valid(self):
        validations = []
        for f in self.form.fields():
            validations.append(f.validate())

        if not all(validations):
            return False
        return True

    def login(self):
        """ Will login to the current provider to expose further information
        that could be useful in subsequent views. This is optional and
        not intended to fail if not defined in the inherited classes.
        """
        pass

    def cloud_config(self):
        """ Returns a config suitable to store as a cloud

        Arguments:
        opts: optional arguments to pass to cloud_config
        """
        raise NotImplementedError

    @property
    def default_region(self):
        """ Returns a default region for cloud
        """
        return None

    async def configure_tools(self):
        """ Configure any provider-specific tools.
        """
        pass

    def load(self, cloud_name):
        """ Attempts to load a cloud from juju
        """
        try:
            _cloud = get_cloud(cloud_name)
            self.cloud = cloud_name
            self.endpoint = _cloud.get('endpoint', None)
            self.regions = _cloud.get('regions', {})
        except LookupError:
            raise SchemaErrorUnknownCloud(
                "Unknown cloud: {}, not updating provider attributes".format(
                    cloud_name))

    def save_form(self):
        """ Saves input fields into provider attributes
        """
        for f in self.form.fields():
            setattr(self, f.key, f.widget.value)


class AWS(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'access-key'
        self.cloud_type = 'ec2'
        self.access_key = None
        self.secret_key = None
        self.form = Form([Field(label='AWS Access Key',
                                widget=StringEditor(),
                                key='access-key'),
                          Field(label='AWS Secret Key',
                                widget=StringEditor(),
                                key='secret-key')])

    @property
    def default_region(self):
        return 'us-east-1'

    async def configure_tools(self):
        """ Configure AWS CLI.
        """
        creds = CredentialManager(self.cloud, self.cloud_type, self.credential)
        for key, value in creds.to_dict().items():
            try:
                await arun(['aws', 'configure', '--profile', self.credential],
                           input='{}\n{}\n\n\n'.format(creds['access-key'],
                                                       creds['secret-key']),
                           check=True)
            except CalledProcessError as e:
                app.log.error('Failed to configure AWS CLI profile: {}'.format(
                    e.stderr))
                raise


class MAAS(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'oauth1'
        self.cloud_type = 'maas'
        self.endpoint = None
        self.apikey = None
        self.form = Form(
            [
                Field(
                    label='api endpoint (http://example.com:5240/MAAS)',
                    widget=StringEditor(),
                    key='endpoint',
                    storable=False,
                    validator=partial(self._has_correct_endpoint)
                ),
                Field(
                    label='api key',
                    widget=StringEditor(),
                    key='maas-oauth',
                    validator=partial(self._has_correct_api_key))
            ]
        )

    def cloud_config(self):
        return {
            'type': 'maas',
            'auth-types': ['oauth1'],
            'endpoint': self.endpoint
        }

    def _has_correct_endpoint(self):
        """ Validates that a ip address or url is passed.
        If url, check to make sure it ends in the /MAAS endpoint
        """
        endpoint = self.endpoint.value
        # Is URL?
        if endpoint.startswith('http'):
            url = urlparse(endpoint)
            if not url.netloc:
                return (False,
                        "Unable to determine the web address, "
                        "please use the format of "
                        "http://maas-server.com:5240/MAAS")
            else:
                if 'MAAS' not in url.path:
                    self.endpoint.value = urljoin(url.geturl(), "MAAS")
                return (True, None)
        elif is_valid_hostname(endpoint):
            # Looks like we just have a domain name
            self.endpoint.value = urljoin("http://{}:5240".format(endpoint),
                                          "MAAS")
            return (True, None)
        else:
            try:
                # Check if valid IPv4 address, add default scheme, api
                # endpoint
                ip = endpoint.split(':')
                port = '5240'
                if len(ip) == 2:
                    ip, port = ip
                else:
                    ip = ip.pop()
                ipaddress.ip_address(ip)
                self.endpoint.value = urljoin(
                    "http://{}:{}".format(ip, port), "MAAS")
                return (True, None)
            except ValueError:
                # Pass through to end so we can let the user know to use the
                # proper http://maas-server.com/MAAS url
                pass
        return (False,
                "Unable to validate that this entry is "
                "the correct format. Please use  the format of "
                "http://maas-server.com:5240/MAAS")

    def _has_correct_api_key(self):
        """ Validates MAAS Api key
        """
        key = self.apikey.value.split(':')
        if len(key) != 3:
            return (
                False,
                "Could not determine tokens, usually indicates an "
                "error with the format of the API KEY. That format "
                "should be 'aaaaa:bbbbb:cccc'. Please visit your MAAS user "
                "preferences page to grab the correct API Key: "
                "http://<maas-server>:5240/MAAS/account/prefs/")
        return (True, None)


class Localhost(BaseProvider):
    def __init__(self):
        super().__init__()
        self.cloud_type = 'lxd'
        self.network_interface = None
        self.form = Form([Field(
            label='network interface to create a LXD bridge for',
            widget=SelectorHorizontal(get_physical_network_interfaces()),
            key='network-interface',
            storable=False
        )])


class Azure(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'service-principal-secret'
        self.cloud_type = 'azure'
        self.application_id = None
        self.subscription_id = None
        self.application_password = None
        self.form = Form([
            Field(
                label='application id',
                widget=StringEditor(),
                key='appnlication-id'
            ),
            Field(
                label='subscription id',
                widget=StringEditor(),
                key='subscription-id'
            ),
            Field(
                label='application password',
                widget=PasswordEditor(),
                key='application-password'
            )
        ])


class Google(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'oauth2'
        self.cloud_type = 'gce'
        self.private_key = None
        self.project_id = None
        self.client_id = None
        self.client_email = None
        self.form = Form(
            [Field(
                label='private key',
                widget=StringEditor(),
                key='private-key'
            ),
                Field(
                label='client id',
                widget=StringEditor(),
                key='client-id'
            ),
                Field(
                label='client email',
                widget=StringEditor(),
                key='client-email'
            ),
                Field(
                label='project id',
                widget=StringEditor(),
                key='project-id'
            )]
        )


class CloudSigma(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = 'cloudsigma'
        self.username = None
        self.password = None
        self.form = Form([
            Field(
                label='username',
                widget=StringEditor(),
                key='username'
            ),
            Field(
                label='password',
                widget=StringEditor(),
                key='password'
            )
        ])


class Joyent(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = 'joyent'
        self.sdc_user = None
        self.sdc_key_id = None
        self.private_key = None
        self.algorithm = None
        self.form = Form([
            Field(
                label='sdc user',
                widget=StringEditor(),
                key='sdc-user'
            ),
            Field(
                label='sdc key id',
                widget=StringEditor(),
                key='sdc-key-id'
            ),
            Field(
                label='private key',
                widget=StringEditor(),
                key='private-key'
            ),
            Field(
                label='algorithm',
                widget=StringEditor(default='rsa-sha256'),
                key='algorithm'
            )]
        )


class OpenStack(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = 'openstack'
        self.username = None
        self.password = None
        self.domain_name = None
        self.project_domain_name = None
        self.access_key = None
        self.secret_key = None

        self.form = Form([
            Field(
                label='username',
                widget=StringEditor(),
                key='username'
            ),
            Field(
                label='password',
                widget=PasswordEditor(),
                key='password'
            ),
            Field(
                label='domain name',
                widget=StringEditor(),
                key='domain-name'
            ),
            Field(
                label='project domain name',
                widget=StringEditor(),
                key='project-domain-name'
            ),
            Field(
                label='access key',
                widget=StringEditor(),
                key='access-key'
            ),
            Field(
                label='secret key',
                widget=StringEditor(),
                key='secret-key'
            )])


class VSphere(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = 'vsphere'
        self.endpoint = None
        self.user = None
        self.password = None
        self.form = Form([
            Field(
                label='api endpoint',
                widget=StringEditor(),
                key='endpoint',
                storable=False
            ),
            Field(
                label='user',
                widget=StringEditor(),
                key='user'
            ),
            Field(
                label='password',
                widget=PasswordEditor(),
                key='password'
            )
        ])

    def login(self):
        if self.authenticated:
            return

        cm = CredentialManager(self.cloud, self.cloud_type, self.credential)
        self.client = VSphereClient(host=self.endpoint,
                                    **cm.to_dict())

        try:
            self.client.login()
            self.authenticated = True
        except VSphereInvalidLogin:
            raise

    def get_datacenters(self):
        """ Grab datacenters that will be used at this clouds regions
        """
        if not self.authenticated:
            self.login()

        return [dc.name for dc in self.client.get_datacenters()]

    def cloud_config(self):
        config = {
            'type': 'vsphere',
            'auth-types': [self.auth_type],
            'endpoint': self.endpoint,
            'regions': {}
        }
        for dc in self.get_datacenters():
            config['regions'][dc] = {self.endpoint}
        return config


class Oracle(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = 'oracle'
        self.identity_domain = None
        self.password = None
        self.username = None
        self.form = Form([
            Field(
                label='identity domain',
                widget=StringEditor(),
                key='identity-domain'
            ),
            Field(
                label='username or e-mail',
                widget=StringEditor(),
                key='username'
            ),
            Field(
                label='password',
                widget=PasswordEditor(),
                key='password'
            )
        ])


Schema = [
    ('ec2', AWS),
    ('maas', MAAS),
    ('azure', Azure),
    ('gce', Google),
    ('cloudsigma', CloudSigma),
    ('joyent', Joyent),
    ('openstack', OpenStack),
    ('rackspace', OpenStack),
    ('vsphere', VSphere),
    ('oracle', Oracle),
    ('localhost', Localhost),
    ('lxd', Localhost),
]


class SchemaError(Exception):
    def __init__(self, cloud):
        super().__init__(
            "Unable to find credentials for {}, "
            "you can double check what credentials you "
            "do have available by running "
            "`juju credentials`. Please see `juju help "
            "add-credential` for more information.".format(
                cloud))


class SchemaErrorUnknownCloud(Exception):
    def __init__(self, cloud):
        super().__init__(
            "Unable to find cloud for {}, "
            "you can double check that cloud exists by running "
            "`juju clouds`. Please see `juju help "
            "clouds` for more information.".format(
                cloud))


def load_schema(cloud):
    """ Loads a schema
    """
    for s in Schema:
        k, v = s
        if cloud == k:
            return v()
    raise SchemaError(cloud)


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
        ('_auth-type', 'userpass'),
        ('host', ("vcenter api-endpoint", StringEditor())),
        ('user', ("vcenter username", StringEditor())),
        ('password', ("vcenter password", PasswordEditor())),
        ('regions', ("datacenter", StringEditor())),
        ('external-network', StringEditor())
    ])),
    ('manual', OrderedDict([
        ('bootstrap-host', StringEditor()),
        ('bootstrap-user', StringEditor()),
        ('use-sshstorage', YesNo())
    ])),
])
