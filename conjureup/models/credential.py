""" Credential Module
"""
from conjureup.juju import get_cloud_types_by_name, get_credential


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
            self.credential = get_credential(self.cloud,
                                             self.credential_name)
        except:
            raise Exception(
                "Could not find credential({}) for cloud({})".format(
                    self.credential_name,
                    self.cloud))

    def to_dict(self):
        """ Returns dictionary of credentials
        """
        raise NotImplementedError

    @classmethod
    def check_cloud_type(cls, credential_cloud_type):
        return credential_cloud_type == cls.CLOUD_TYPE


class VSphereCredential(BaseCredential):
    CLOUD_TYPE = 'vsphere'

    def to_dict(self):
        return {'username': self.credential['user'],
                'password': self.credential['password']}


class CredentialManager:
    CREDENTIALS = [VSphereCredential]

    def __init__(self, cloud, cloud_type, credential_name):
        self.credential_name = credential_name
        self.cloud = cloud
        self.cloud_type = cloud_type
        self.credential_obj = self._get_credential_object()

    def _get_credential_object(self):
        cloud_type = get_cloud_types_by_name().get(self.cloud_type)
        for credential in self.CREDENTIALS:
            if credential.check_cloud_type(cloud_type):
                return credential(self.cloud,
                                  self.credential_name)
        raise CredentialManagerInvalidCloudType

    def to_dict(self):
        return self.credential_obj.to_dict()
