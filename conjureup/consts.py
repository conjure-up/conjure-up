from enum import Enum

UNSPECIFIED_SPELL = '_unspecified_spell'
JAAS_CLOUDS = {'ec2', 'azure', 'gce'}
JAAS_DOMAIN = 'jimm.jujucharms.com'
JAAS_ENDPOINT = JAAS_DOMAIN + ':443'


class cloud_types(Enum):
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
    AFTER_DEPLOY = 'after-deploy'
