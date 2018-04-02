import yaml


class ConjurefileException(Exception):
    pass


class Conjurefile(dict):
    """
    spell: canonical-kubernetes
    provider: localhost
    addons:
      helm:
        version: v2.8.1
    steps:
      select-network:
        networkplugin: "calico"

    on_complete:
      - cat /etc/uptime

    proxy:
      http-proxy: http://localhost:5252
      https-proxy: http://localhost:5252
      apt-http-proxy: http://localhost:5252
      apt-https-proxy: http://localhost:5252
      no-proxy: jujucharms.com
    """

    def __init__(self, data):
        super().__init__(data)

    @classmethod
    def load(cls, path):
        """ Load spell metadata
        """
        return Conjurefile(
            yaml.safe_load(path.read_text()))

    def merge_argv(self, argv):
        """
        Overrides options in the conjurefile with
        those passed in via sys.argv
        """
        argv_dict = vars(argv)
        for k, v in argv_dict.items():
            if v and k in self:
                self[k] = v
