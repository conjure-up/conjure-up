""" Credential Module
"""
import inspect
import sys

from conjureup.juju import get_credential


class CredentialManagerInvalidCloudType(Exception):
    """ Unable to match a credential to the cloud type
    """
    pass


class BaseCredential:
    """ Base credential for all clouds
    """
    CLOUD_TYPE = None

    def __init__(self, cloud, credential_name):
        self.credential_name = credential_name
        self.cloud = cloud
        self.credential = None
        self.load()

    def load(self):
        try:
            self._credential = get_credential(self.cloud,
                                              self.credential_name)
        except:
            raise Exception(
                "Could not find credential({}) for cloud({})".format(
                    self.credential_name,
                    self.cloud))

    def to_dict(self):
        """ Returns dictionary of credential data.
        """
        return dict(self._credential)

    @classmethod
    def check_cloud_type(cls, credential_cloud_type):
        return credential_cloud_type == cls.CLOUD_TYPE


class AWSCredential(BaseCredential):
    CLOUD_TYPE = 'ec2'

    @property
    def access_key(self):
        return self._credential['access-key']

    @property
    def secret_key(self):
        return self._credential['secret-key']


class MAASCredential(BaseCredential):
    CLOUD_TYPE = 'maas'


class LocalhostCredential(BaseCredential):
    CLOUD_TYPE = 'localhost'


class AzureCredential(BaseCredential):
    CLOUD_TYPE = 'azure'


class GoogleCredential(BaseCredential):
    CLOUD_TYPE = 'gce'


class CloudSigmaCredential(BaseCredential):
    CLOUD_TYPE = 'cloudsigma'


class JoyentCredential(BaseCredential):
    CLOUD_TYPE = 'joyent'


class OpenStackCredential(BaseCredential):
    CLOUD_TYPE = 'openstack'


class VSphereCredential(BaseCredential):
    CLOUD_TYPE = 'vsphere'

    @property
    def username(self):
        return self._credential['user']

    @property
    def password(self):
        return self._credential['password']

    def to_dict(self):
        return {'username': self.username,
                'password': self.password}


class CredentialManager:
    @classmethod
    def get_credential(cls, cloud, cloud_type, credential_name):
        mod = sys.modules[__name__]

        def _is_cred(candidate):
            return (inspect.isclass(candidate) and
                    issubclass(candidate, BaseCredential) and
                    candidate is not BaseCredential)

        for name, credential in inspect.getmembers(mod, _is_cred):
            if credential.check_cloud_type(cloud_type):
                return credential(cloud, credential_name)

        raise CredentialManagerInvalidCloudType
