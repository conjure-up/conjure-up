import textwrap
from pathlib import Path

import yaml
from melddict import MeldDict


class ConjurefileException(Exception):
    pass


class Conjurefile(MeldDict):
    """
    # (Required) Name of spell to summon. This can be in the form
    # of a GitHub repo, filesystem path, or a pre-packaged spell.
    #
    # Choose One of:
    #
    # A prebundled spell:
    # spell: canonical-kubernetes

    # A GitHub Repo
    # spell: battlemidget/ghost
    #
    # A local filesystem path
    # spell: ~/spells/hadoop-spark

    # (Required) The cloud to use. This can be any cloud listed here:
    # https://jujucharms.com/docs/stable/clouds#listing-available-clouds
    # cloud: localhost

    # A provider can also be a cloud/region
    # cloud: aws/us-east-1
    #
    # (Optional) Set any addons you wish to deploy.
    #

    # (Optional) Controller name. This can be any arbitrary name of your Juju
    # controller.
    # controller: us-dc1

    # (Optional) Model name. This can be any arbitrary name of your Juju Model
    # model: k8s-1

    # For the Kubernetes spell you may want Helm installed so you can deploy
    # charts to the cluster.
    # addons:
    #  helm:
    #    01_install-helm:
    #      helm_version: v2.8.1

    # (Optional) Customize any of the steps that are run once the spell is
    # deployed
    #
    # steps:
    #  01_select-network:
    #    networkplugin: "flannel"

    # (Optional) Execute a custom script once everything is deployed. This
    # could be anything you choose, whether it's deploying a Helm chart, to
    # scaling out your cluster.
    #
    # on-complete: ./my_custom_script.sh

    # Debugging
    debug: false

    # Reporting
    # no-track: false
    # no-report: false
    """

    def __init__(self):
        initial_data = yaml.safe_load(
            textwrap.dedent(Conjurefile.__doc__.strip()))
        super().__init__(self.add(initial_data))

    @classmethod
    def print_tpl(cls):
        """ Prints a Conjurefile template
        """
        print(textwrap.dedent(Conjurefile.__doc__))

    @classmethod
    def load(cls, paths):
        """ Load spell metadata

        Arguments:
        paths: list of path names to pull in for updating
               conjurefile
        """
        cf = Conjurefile()
        for p in paths:
            try:
                new_data = yaml.safe_load(p.read_text())
                if not isinstance(new_data, dict):
                    raise ValueError('contents are not a mapping')
            except Exception as e:
                raise ValueError('Unable to load {}: {}'.format(p, e))
            cf += new_data
        return cf

    def merge_argv(self, argv, defaults):
        """
        Overrides options in the conjurefile with
        those passed in via sys.argv
        """
        argv_dict = vars(argv)
        defaults_dict = vars(defaults)
        for k, v in argv_dict.items():
            fk = k.replace('_', '-')
            if v == defaults_dict[k]:
                # opt was not overridden on the CLI, so file takes precedence
                # but we still want to set it to ensure we use the default
                self[fk] = self.get(fk, v)
                if isinstance(defaults_dict[k], Path):
                    self[fk] = Path(self[fk])
            else:
                # opt was overridden, so CLI takes precedence
                self[fk] = v

    @property
    def is_valid(self):
        """
        Returns whether this conjurefile has minimum set of requirements to run
        a headless install
        """
        if 'cloud' in self and self['cloud']:
            return True
        return False

    def has_step(self, step_name):
        """ Verifies a step name is defined
        """
        if self.steps and step_name in self.steps:
            return True
        return False

    @property
    def steps(self):
        """ Conjurefile defined steps
        """
        return self.get('steps', {})

    def step(self, step_name, key, addon_name):
        """ Returns the step's value
        """
        # Check addons first
        is_addon = self.addons.get(addon_name, None)
        if is_addon and step_name in is_addon:
            return is_addon[step_name].get(
                key.lower(), None)

        # Check spell steps
        if not self.has_step(step_name):
            return None
        return self.steps[step_name].get(
            key.lower(), None)

    def addon(self, addon_name):
        """ Return addon name step
        """
        return self.addons.get(addon_name, None)

    @property
    def addons(self):
        """ Conjurefile defined addons
        """
        return self.get('addons', {})
