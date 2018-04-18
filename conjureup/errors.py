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
