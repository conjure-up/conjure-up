The specification of an apt-juju package:

## UI

The UI should process a list of questions pulled from the `config.yaml` of a charm.

Utilizing `config.yaml` from a charm we then decide on which configuration options
make sense to be edited and what our recommended setting would be initially.

## Install

The installation portion should provide an automated deployment like the OpenStack
Installer's single install method.

The installation should also be able to detect whether an existing Juju environment
exists and make a few assumptions based on the type of environment (MAAS, Local, AWS).

If no previous juju environment exists the installation should automatically create
one defaulting to a Local/LXD installation. Could also provide a install type selection
screen to allow the user to deploy to an existing MAAS.
