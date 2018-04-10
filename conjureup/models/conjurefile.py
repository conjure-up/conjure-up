import textwrap

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
    #    version: v2.8.1

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
    # on_complete: ./my_custom_script.sh

    # Debugging
    debug: true

    # Reporting
    # notrack: false
    # noreport: false
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
            cf += yaml.safe_load(p.read_text())
        return cf

    def merge_argv(self, argv):
        """
        Overrides options in the conjurefile with
        those passed in via sys.argv
        """
        posargs = ['spell', 'cloud', 'controller', 'model']
        argv_dict = vars(argv)
        for k, v in argv_dict.items():
            if v and k in self:
                self[k] = v
            if k in posargs:
                self[k] = v

    @property
    def is_valid(self):
        """
        Returns whether this conjurefile has minimum set of requirements to run
        a headless install
        """
        if self.get('spell', None) and self.get('cloud', None):
            return True
        return False
