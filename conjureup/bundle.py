"""
Bundle class for providing some common utilities when manipulating the bundle
spec
"""
from collections import Mapping
from itertools import chain

import yaml

from conjureup.consts import spell_types


class BundleInvalidApplication(Exception):
    pass


class BundleInvalidFragment(Exception):
    pass


class BundleApplicationFragment(dict):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)
        self._constraints = self.get('constraints', "")
        self._num_units = int(self.get('num_units', 0))
        self._options = self.get('options', {})

    @property
    def constraints(self):
        """ Set/Get application constraints
        """
        return self._constraints

    @constraints.setter
    def constraints(self, val):
        self._constraints = val

    @property
    def num_units(self):
        """ Set/Get number of units for application
        """
        return self._num_units

    @num_units.setter
    def num_units(self, val):
        self._num_units = val

    @property
    def options(self):
        """ Set/Get application options
        """
        return self._options

    @options.setter
    def options(self, val):
        self._options.update(val)

    @property
    def charm(self):
        """ Provides charmstore endpoint
        """
        if 'charm' not in self:
            raise BundleInvalidFragment(
                "Unable to locate charm: in bundle fragment: {}".format(
                    self.fragment))
        return self['charm']

    @property
    def is_subordinate(self):
        """ Returns if application fragment is a charm subordinate
        """
        if self.num_units == 0:
            return True
        return False

    @property
    def to(self):
        """ Returns machine placement
        """
        return self.get('to', [])

    def to_dict(self):
        items = {
            'charm': self.charm,
            'num_units': self.num_units
        }
        if self.options:
            items['options'] = self.options
        if self.to:
            items['to'] = self.to
        if self.constraints:
            items['constraints'] = self.constraints

        expose = self.get('expose', False)
        if expose:
            items['expose'] = expose
        return items


class SnapBundleApplicationFragment(dict):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)
        self._snap = self.get('snap', name)
        self._channel = self.get('channel', 'stable')
        self._options = self.get('options', {})
        self._confinement = self.get('confinement', None)

    @property
    def snap(self):
        """ Set/Get snap
        """
        return self._snap

    @snap.setter
    def snap(self, val):
        self._snap = val

    @property
    def confinement(self):
        """ Get confinment
        """
        return self._confinement

    @confinement.setter
    def confinement(self, val):
        """ Set confinement value
        """
        self._confinement = val

    @property
    def channel(self):
        """ Set/Get snap channel
        """
        return self._channel

    @channel.setter
    def channel(self, val):
        self._channel = val

    @property
    def options(self):
        """ Set/Get application options
        """
        return self._options

    @options.setter
    def options(self, val):
        self._options.update(val)

    def to_dict(self):
        return self


class Bundle(dict):
    def __init__(self, bundle, spell_type=spell_types.JUJU):
        self.spell_type = spell_type
        super().__init__(self._normalize_bundle(bundle))

    def _normalize_bundle(self, bundle):
        """ Normalizes bundle for things
        like applications vs. services
        """
        new_bundle = {}
        for k, v in bundle.items():
            if k == 'services':
                new_bundle['applications'] = v
            else:
                new_bundle[k] = v
        return new_bundle

    def to_yaml(self):
        """ Returns yaml dump of bundle
        """
        return yaml.dump(self.to_dict(),
                         default_flow_style=False)

    def to_dict(self):
        """ Returns dictionary representation
        """
        return dict(self)

    def _merge_dicts(self, *dicts):
        """
        Return a new dictionary that is the result of merging the arguments
        together.
        In case of conflicts, later arguments take precedence over earlier
        arguments.
        ref:  http://stackoverflow.com/a/8795331/3170835
        """
        updated = {}
        # grab all keys
        keys = set()

        for d in dicts:
            keys = keys.union(set(d))

        for key in keys:
            values = [d[key] for d in dicts if key in d]
            # which ones are mapping types? (aka dict)
            maps = [value for value in values
                    if isinstance(value, Mapping)]
            lists = [value for value in values
                     if isinstance(value, (list, tuple))]
            if maps:
                # if we have any mapping types, call recursively to merge them
                updated[key] = self._merge_dicts(*maps)
            elif lists:
                # if any values are lists, we want to merge them
                # (non-recursively) first, ensure all values are lists
                for i in range(len(values)):
                    if not isinstance(values[i], (list, tuple)):
                        values[i] = [values[i]]
                # then, merge all of the lists into a single list
                updated[key] = list(chain.from_iterable(values))
            else:
                # otherwise, just grab the last value we have, since later
                # arguments take precedence over earlier arguments
                updated[key] = values[-1]
        return updated

    def _subtract_dicts(self, *dicts):
        """
        Return a new dictionary that is the result of subtracting each dict
        from the previous.  Except for mappings, the values of the subsequent
        are ignored and simply all matching keys are removed.  If the value is
        a mapping, however, then only the keys from the sub-mapping are
        removed, recursively.
        """
        result = self._merge_dicts(dicts[0], {})  # make a deep copy
        for d in dicts[1:]:
            for key, value in d.items():
                if key not in result:
                    continue
                if isinstance(value, Mapping):
                    result[key] = self._subtract_dicts(result[key], value)
                    if not result[key]:
                        # we removed everything from the mapping,
                        # so remove the whole thing
                        del result[key]
                elif isinstance(value, (list, tuple)):
                    if not isinstance(result[key], (list, tuple)):
                        # if the original value isn't a list, then remove it
                        # if it matches any of the values in the given list
                        if result[key] in value:
                            del result[key]
                    else:
                        # for lists, remove any matching
                        # items (non-recursively)
                        result[key] = [item
                                       for item in result[key]
                                       if item not in value]
                        if not result[key]:
                            # we removed everything from the list,
                            # so remove the whole thing
                            del result[key]
                else:
                    del result[key]
        return result

    def apply(self, fragment):
        """ Applies bundle fragment to bundle, overwriting
        any preexisting values
        """
        _fragment = self._normalize_bundle(fragment)
        result = self._merge_dicts(self, _fragment)
        self.clear()
        self.update(result)

    def subtract(self, fragment):
        """ Subtracts a bundle fragment from existing bundle
        """
        _fragment = self._normalize_bundle(fragment)
        result = self._subtract_dicts(self, _fragment)
        self.clear()
        self.update(result)

    @property
    def applications(self):
        """ Returns list of applications/services
        """
        _applications = []
        for app in self['applications'].keys():
            _applications.append(self._get_application_fragment(app))
        return _applications

    @property
    def machines(self):
        """ Returns defined machines
        """
        return self.get('machines', [])

    @property
    def relations(self):
        """ Returns application relations
        """
        return self.get('relations', [])

    def _get_application_fragment(self, app_name):
        """ Returns bundle fragment
        """
        if app_name not in self['applications']:
            raise BundleInvalidApplication(
                "Unable find a bundle fragment for: {}".format(app_name))
        _fragment = self['applications'][app_name]
        if self.spell_type == spell_types.SNAP:
            return SnapBundleApplicationFragment(app_name, _fragment)
        return BundleApplicationFragment(app_name, _fragment)
