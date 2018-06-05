class MessageException(Exception):
    message = "General error"

    def __init__(self, *args, **kwargs):
        self.message = self.message.format(*args, **kwargs)
        super().__init__(self.message)


class BootstrapError(Exception):
    "An error when bootstrapping a new controller"


class BootstrapInterrupt(BootstrapError):
    "The bootstrap was interrupted by the user"


class ControllerNotFoundException(Exception):
    "An error when a controller can't be found in juju's config"


class DeploymentFailure(Exception):
    "A failure from a deployed model"


class JujuBinaryNotFound(Exception):
    "A failure finding juju or juju-wait executable"


class AppConfigAttributeError(Exception):
    "A failure to lookup attribute in app_config object"


class MAASConfigError(Exception):
    "An error representing a MAAS configuration issue."


class SchemaError(MessageException):
    message = "General Schema error"


class SchemaCloudError(SchemaError):
    message = ("Unable to find cloud for {}, you can double check that "
               "cloud exists by running `juju clouds`. Please see "
               "`juju help clouds` for more information.")


class SchemaCredentialError(SchemaError):
    message = ("Unable to find credentials for {}, you can double check "
               "what credentials you do have available by running "
               "`juju credentials`. Please see `juju help add-credential` "
               "for more information.")


class LXDError(MessageException):
    message = "General LXD error"


class LXDBinaryNotFoundError(LXDError):
    message = ("LXD not found.  To install, see "
               "https://docs.conjure-up.io/devel/en/#users-of-lxd")


class LXDCompatibilityError(LXDError):
    message = ("LXD version 3.0.0 or greater is required. "
               "To install or upgrade, see "
               "https://docs.conjure-up.io/devel/en/#users-of-lxd")


class LXDParseError(LXDCompatibilityError):
    message = ("Unable to parse JSON output from LXD, does "
               "`{} query --wait -X GET /1.0` "
               "return info about the LXD server?")


class LXDNetworkError(LXDError):
    message = ("Unable to find IPv4-only network bridge for LXD. "
               "For information on configuring networking for LXD, see "
               "https://docs.conjure-up.io/devel/en/#users-of-lxd")


class LXDStorageError(LXDError):
    message = ("Unable to find a storage pool for LXD. "
               "For information on configuring storage for LXD, see "
               "https://docs.conjure-up.io/devel/en/#users-of-lxd")
