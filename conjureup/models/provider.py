import ipaddress
import json
from collections import OrderedDict
from functools import partial
from pathlib import Path
from subprocess import CalledProcessError
from urllib.parse import urljoin, urlparse

from pkg_resources import parse_version
from ubuntui.widgets.input import PasswordEditor, StringEditor, YesNo
from urwid import Text

from conjureup import utils
from conjureup.app_config import app
from conjureup.consts import cloud_types
from conjureup.juju import get_cloud
from conjureup.models.credential import CredentialManager
from conjureup.utils import arun, is_valid_hostname
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

    @value.setter
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

    def field(self, key):
        """ Gets widget from field key
        """
        for w in self.fields():
            if key == w.key:
                return w
        return None


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

    async def login(self):
        """ Will login to the current provider to expose further information
        that could be useful in subsequent views. This is optional and
        not intended to fail if not defined in the inherited classes.
        """
        pass

    async def cloud_config(self):
        """ Returns a config suitable to store as a cloud
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
            self.regions = sorted(_cloud.get('regions', {}).keys())
        except LookupError:
            raise SchemaErrorUnknownCloud(
                "Unknown cloud: {}, not updating provider attributes".format(
                    cloud_name))

    async def save_form(self):
        """ Saves input fields into provider attributes, normalizing any keys,
        currently those with hyphens.
        """
        for f in self.form.fields():
            key = f.key.replace('-', '_')
            setattr(self, key, f.widget.value)


class AWS(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'access-key'
        self.cloud_type = cloud_types.AWS
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
        cred = CredentialManager.get_credential(self.cloud,
                                                self.cloud_type,
                                                self.credential)
        try:
            ret, _, _ = await arun(['aws', 'configure', 'list',
                                    '--profile', self.credential], check=False)
            if ret != 0:
                await arun(['aws', 'configure', '--profile', self.credential],
                           input='{}\n{}\n\n\n'.format(cred.access_key,
                                                       cred.secret_key),
                           check=True)
        except CalledProcessError as e:
            app.log.error('Failed to configure AWS CLI profile: {}'.format(
                e.stderr))
            raise


class MAAS(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'oauth1'
        self.cloud_type = cloud_types.MAAS
        self.form = Form(
            [
                Field(
                    label='API Endpoint (http://example.com:5240/MAAS)',
                    widget=StringEditor(),
                    key='endpoint',
                    storable=False,
                    validator=partial(self._has_correct_endpoint)
                ),
                Field(
                    label='API Key',
                    widget=StringEditor(),
                    key='maas-oauth',
                    validator=partial(self._has_correct_api_key))
            ]
        )

    async def cloud_config(self):
        return {
            'type': 'maas',
            'auth-types': ['oauth1'],
            'endpoint': self.endpoint
        }

    def _has_correct_endpoint(self):
        """ Validates that a ip address or url is passed.
        If url, check to make sure it ends in the /MAAS endpoint
        """
        field = self.form.field('endpoint')
        endpoint = field.value
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
                    field.value = urljoin(url.geturl(), "MAAS")
                return (True, None)
        elif is_valid_hostname(endpoint):
            # Looks like we just have a domain name
            field.value = urljoin("http://{}:5240".format(endpoint),
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
                field.value = urljoin(
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
        field = self.form.field('maas-oauth')
        key = (field.value or '').split(':')
        if len(key) != 3:
            return (
                False,
                "Could not determine tokens, usually indicates an "
                "error with the format of the API KEY. That format "
                "should be 'aaaaa:bbbbb:cccc'. Please visit your MAAS user "
                "preferences page to grab the correct API Key: "
                "http://<maas-server>:5240/MAAS/account/prefs/")
        return (True, None)


class LocalhostError(Exception):
    pass


class LocalhostJSONError(Exception):
    pass


class Localhost(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'interactive'
        self.cloud_type = cloud_types.LOCALHOST
        self.network_interface = None
        self.minimum_support_version = parse_version('2.17')
        self.available = False
        self.lxc_bin = None
        self._set_lxd_dir_env()

    def _set_lxd_dir_env(self):
        """ Sets and updates correct environment
        """
        if Path('/snap/bin/lxd').exists():
            self.lxd_socket_dir = Path('/var/snap/lxd/common/lxd')
            app.env['LXD_DIR'] = str(self.lxd_socket_dir)
            self.lxc_bin = '/snap/bin/lxc'
        elif Path('/usr/bin/lxd').exists():
            self.lxd_socket_dir = Path('/var/lib/lxd')
            app.env['LXD_DIR'] = str(self.lxd_socket_dir)
            self.lxc_bin = '/usr/bin/lxc'
        else:
            raise LocalhostError(
                "Unable to find a lxd binary. Make sure `snap info lxd` "
                "shows as installed, otherwise, run `sudo snap "
                "install lxd` and restart conjure-up.")
        app.log.debug("LXD environment set: binary {} lxd_dir {}".format(
            self.lxc_bin, self.lxd_socket_dir))

    async def query(self, segment='', method="GET"):
        """ Query lxc api server

        Example: lxd v2.17: lxc query /1.0 | jq .
        """
        if segment.startswith('/1.0'):
            url = str(segment)
        else:
            segment_prefix = Path('/1.0')
            url = str(segment_prefix / segment)
        try:
            cmd = [self.lxc_bin, 'query', '--wait', url]
            app.log.debug("LXD query cmd: {}".format(" ".join(cmd)))
            _, out, err = await utils.arun(cmd)
            return json.loads(out)
        except json.decoder.JSONDecodeError:
            err = ("Unable to parse JSON output from LXD, does "
                   "`{} query --wait -X GET /1.0` "
                   "return info about the LXD server?".format(self.lxc_bin))
            app.log.error(err)
            raise LocalhostJSONError(err)
        except FileNotFoundError as e:
            app.log.error(e)
            raise
        except CalledProcessError as e:
            app.log.error(e)
            raise LocalhostError(e)

    async def get_networks(self):
        """ Grabs lxc network bridges from api
        """
        networks = await self.query('networks')
        bridges = OrderedDict()
        for net in networks:
            net_info = await self.query(net)
            if 'config' in net_info and 'ipv6.address' in net_info['config']:
                # Juju doesn't support ipv6
                if net_info['config']['ipv6.address'] != 'none':
                    continue
            if net_info['type'] == "bridge":
                bridges[net_info['name']] = net_info
                if net_info['name'] == 'lxdbr0':
                    bridges.move_to_end('lxdbr0', last=False)
        return bridges

    async def get_storage_pools(self):
        """ Grabs lxc storage pools from api
        """
        pools = await self.query('storage-pools')
        _pools = OrderedDict()
        for pool in pools:
            pool_path = Path(pool)
            _pools[pool_path.stem] = await self.query(pool)
            if pool_path.stem == 'default':
                _pools.move_to_end('default', last=False)
        return _pools

    async def is_server_compatible(self):
        """ Waits and checks if LXD server becomes available

        We'll want to loop here and ignore most errors until have retries have
        been met
        """
        try:
            out = await self.query()
            server_ver = out['environment']['server_version']
            return parse_version(server_ver) >= self.minimum_support_version
        except (LocalhostError, LocalhostJSONError, FileNotFoundError):
            return False

    async def is_client_compatible(self):
        """ Checks if LXC version is compatible with conjure-up
        """
        try:
            _, out, err = await utils.arun([self.lxc_bin, '--version'])
            server_ver = out.strip()
            return parse_version(server_ver) >= self.minimum_support_version
        except CalledProcessError as e:
            app.log.error(e)
            raise LocalhostError(e)


class Azure(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'service-principal-secret'
        self.cloud_type = cloud_types.AZURE
        self.form = Form([
            Field(
                label='Application ID',
                widget=StringEditor(),
                key='application-id'
            ),
            Field(
                label='Subscription ID',
                widget=StringEditor(),
                key='subscription-id'
            ),
            Field(
                label='Application Password',
                widget=PasswordEditor(),
                key='application-password'
            )
        ])


class Google(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'oauth2'
        self.cloud_type = cloud_types.GCE
        self.form = Form(
            [Field(
                label='Private Key',
                widget=StringEditor(),
                key='private-key'
            ),
                Field(
                label='Client ID',
                widget=StringEditor(),
                key='client-id'
            ),
                Field(
                label='Client Email',
                widget=StringEditor(),
                key='client-email'
            ),
                Field(
                label='Project ID',
                widget=StringEditor(),
                key='project-id'
            )]
        )


class CloudSigma(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = cloud_types.CLOUDSIGMA
        self.form = Form([
            Field(
                label='Username',
                widget=StringEditor(),
                key='username'
            ),
            Field(
                label='Password',
                widget=StringEditor(),
                key='password'
            )
        ])


class Joyent(BaseProvider):

    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = cloud_types.JOYENT
        self.form = Form([
            Field(
                label='SDC User',
                widget=StringEditor(),
                key='sdc-user'
            ),
            Field(
                label='SDC Key ID',
                widget=StringEditor(),
                key='sdc-key-id'
            ),
            Field(
                label='Private Key',
                widget=StringEditor(),
                key='private-key'
            ),
            Field(
                label='Algorithm',
                widget=StringEditor(default='rsa-sha256'),
                key='algorithm'
            )]
        )


class OpenStack(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = cloud_types.OPENSTACK

        self.form = Form([
            Field(
                label='Username',
                widget=StringEditor(),
                key='username'
            ),
            Field(
                label='Password',
                widget=PasswordEditor(),
                key='password'
            ),
            Field(
                label='Domain Name',
                widget=StringEditor(),
                key='domain-name'
            ),
            Field(
                label='Project Domain Name',
                widget=StringEditor(),
                key='project-domain-name'
            ),
            Field(
                label='Access Key',
                widget=StringEditor(),
                key='access-key'
            ),
            Field(
                label='Secret Key',
                widget=StringEditor(),
                key='secret-key'
            )])


class VSphere(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = cloud_types.VSPHERE
        self.form = Form([
            Field(
                label='API Endpoint',
                widget=StringEditor(),
                key='endpoint',
                storable=False
            ),
            Field(
                label='Username',
                widget=StringEditor(),
                key='user'
            ),
            Field(
                label='Password',
                widget=PasswordEditor(),
                key='password'
            )
        ])
        self._datacenters = None

    async def login(self):
        if self.authenticated:
            return

        cred = CredentialManager.get_credential(self.cloud,
                                                self.cloud_type,
                                                self.credential)
        self.client = VSphereClient(cred, self.endpoint)

        try:
            await app.loop.run_in_executor(None, self.client.login)
            self.authenticated = True
        except VSphereInvalidLogin:
            raise

    async def get_datacenters(self):
        """ Grab datacenters that will be used at this clouds regions
        """
        if self._datacenters is not None:
            return self._datacenters  # use cached datacenters

        if not self.authenticated:
            await self.login()

        self._datacenters = await app.loop.run_in_executor(
            None, self.client.get_datacenters)
        return self._datacenters

    async def cloud_config(self):
        config = {
            'type': 'vsphere',
            'auth-types': [self.auth_type],
            'endpoint': self.endpoint,
            'regions': {}
        }
        for dc in await self.get_datacenters():
            config['regions'][dc.name] = {'endpoint': self.endpoint}
        # this is a new cloud, so we have to
        # populate the in-memory list of regions
        self.regions = sorted(config['regions'].keys())
        return config


class Oracle(BaseProvider):
    def __init__(self):
        super().__init__()
        self.auth_type = 'userpass'
        self.cloud_type = cloud_types.ORACLE
        self.form = Form([
            Field(
                label='Identity Domain',
                widget=StringEditor(),
                key='identity-domain'
            ),
            Field(
                label='Username or Email',
                widget=StringEditor(),
                key='username'
            ),
            Field(
                label='Password',
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
