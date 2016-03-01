class CharmModelException(Exception):
    """ Exception in CharmModel """


class CharmModel:
    """ Stores charm/bundle location for juju deploy
    """
    bundle = {
        "key": None,
        "name": None,
        "summary": None,
        "revision": None
    }

    @classmethod
    def key(cls):
        """ Returns key of resource
        """
        return cls.bundle.get('key', None)

    @classmethod
    def name(cls):
        """ Returns name of resource
        """
        return cls.bundle.get('name', None)

    @classmethod
    def summary(cls):
        """ Returns summary of resource
        """
        return cls.bundle.get('summary', None)

    @classmethod
    def revision(cls):
        """ Returns revision of resource
        """
        return cls.bundle.get('revision', None)

    @classmethod
    def to_entity(cls, use_latest=True):
        """ Returns proper entity key to query the charmstore.

        Arguments:
        use_latest: Use latest bundle revision from charmstore

        Returns:
        Formatted entity string suitable for charmstore lookup
        """
        if cls.key() is None:
            raise CharmModelException("Unable to determine bundle path.")
        if use_latest:
            return cls.key()
        else:
            return "{}-{}".format(cls.key(), cls.revision())

    @classmethod
    def to_path(cls):
        """ Returns bundle path suitable for juju deploy <bundle>
        """
        bundle = cls.key()
        if bundle is None:
            raise CharmModelException("Unable to determine bundle")
        if cls.revision() is not None:
            bundle = "{}-{}".format(bundle, cls.revision())
        return "cs:bundle/{}".format(bundle)
