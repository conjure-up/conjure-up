from enum import Enum

UNSPECIFIED_SPELL = '_unspecified_spell'
JAAS_CLOUDS = {'ec2', 'azure', 'gce'}
JAAS_DOMAIN = 'jimm.jujucharms.com'
JAAS_ENDPOINT = JAAS_DOMAIN + ':443'
CUSTOM_PROVIDERS = ['localhost', 'maas', 'vsphere', 'openstack']
ALLOWED_CONSTRAINTS = [
    'arch',
    'container',
    'cpu-cores',
    'cores',
    'cpu-power',
    'mem',
    'root-disk',
    'tags',
    'instance-type',
    'spaces',
    'virt-type'
]


class cloud_types:
    AWS = 'ec2'
    MAAS = 'maas'
    AZURE = 'azure'
    GOOGLE = 'gce'
    GCE = 'gce'
    CLOUDSIGMA = 'cloudsigma'
    JOYENT = 'joyent'
    OPENSTACK = 'openstack'
    RACKSPACE = 'openstack'
    VSPHERE = 'vsphere'
    ORACLE = 'oracle'
    LOCALHOST = 'localhost'
    LOCAL = 'localhost'
    LXD = 'localhost'


class PHASES(Enum):
    VALIDATE_INPUT = 'validate-input'
    AFTER_INPUT = 'after-input'
    BEFORE_DEPLOY = 'before-deploy'
    BEFORE_WAIT = 'before-wait'
    AFTER_DEPLOY = 'after-deploy'
