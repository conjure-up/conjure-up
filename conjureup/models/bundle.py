class BundleModelException(Exception):
    """ Exception in BundleModel """


class BundleModel:
    """ Stores bundle location for juju deploy
    """
    bundle = {
        "key": None,
        "name": None,
        "summary": None,
        "revision": None,
        "location": None,
        "blacklist": [],
        "whitelist": [],
        "recommendedCharms": [],
        "bootstrapSeries": None
    }

    @classmethod
    def key(cls):
        """ Returns key of resource
        """
        return cls.bundle.get('key', None)

    @classmethod
    def location(cls):
        """ Location of bundle, this will override key as
        location can contain namespaced bundles
        """
        return cls.bundle.get('location', None)

    @classmethod
    def bootstrapSeries(cls):
        """ Returns a defined bootstrap-series
        """
        return cls.bundle.get('bootstrapSeries', None)

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
    def whitelist(cls):
        """ Returns whitelisted provider types
        """
        return cls.bundle.get('whitelist', [])

    @classmethod
    def blacklist(cls):
        """ Returns blacklisted provider types
        """
        return cls.bundle.get('blacklist', [])

    @classmethod
    def recommended(cls):
        """ Returns recommended charms
        """
        return cls.bundle.get('recommendedCharms', [])

    @classmethod
    def to_entity(cls, use_latest=True):
        """ Returns proper entity key to query the charmstore.

        Arguments:
        use_latest: Use latest bundle revision from charmstore

        Returns:
        Formatted entity string suitable for charmstore lookup
        """
        if cls.location() is None and cls.key() is None:
            raise BundleModelException("Unable to determine bundle path.")
        if cls.location():
            return cls.location()
        if not use_latest:
            return "{}-{}".format(cls.key(), cls.revision())
        return cls.key()

    @classmethod
    def to_path(cls):
        """ Returns bundle path suitable for juju deploy <bundle>
        """
        bundle = cls.key()
        if bundle is None:
            raise BundleModelException("Unable to determine bundle")
        if cls.revision() is not None:
            bundle = "{}-{}".format(bundle, cls.revision())
        return "cs:bundle/{}".format(bundle)
