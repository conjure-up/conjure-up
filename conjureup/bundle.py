"""
Bundle class for providing some common utilities when manipulating the bundle
spec
"""
from collections import Mapping
from itertools import chain

import yaml


class BundleInvalidApplication(Exception):
    pass


class BundleInvalidFragment(Exception):
    pass


class BundleFragment:
    def __init__(self, name, fragment):
        self.fragment = fragment
        self.name = name

    @property
    def num_units(self):
        return int(self.fragment.get('num_units', 0))

    @property
    def options(self):
        return self.fragment.get('options', {})

    @property
    def charm(self):
        if 'charm' not in self.fragment:
            raise BundleInvalidFragment(
                "Unable to locate charm: in bundle fragment: {}".format(
                    self.fragment))
        return self.fragment['charm']

    @property
    def is_subordinate(self):
        if self.num_units == 0:
            return True
        return False

    @property
    def to(self):
        return self.fragment.get('to', [])

    def to_dict(self):
        items = {
            'charm': self.charm,
            'num_units': self.num_units,
            'options': self.options,
            'to': self.to
        }
        expose = self.fragment.get('expose', False)
        if expose:
            items['expose'] = expose
        return items


class Bundle:
    def __init__(self, bundle):
        self._bundle = self._normalize_bundle(bundle)

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
        return yaml.dump(self._bundle,
                         default_flow_style=False)

    def to_dict(self):
        """ Returns dictionary representation
        """
        return self._bundle

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
        self._bundle = self._merge_dicts(self._bundle, _fragment)

    def subtract(self, fragment):
        """ Subtracts a bundle fragment from existing bundle
        """
        _fragment = self._normalize_bundle(fragment)
        self._bundle = self._subtract_dicts(self._bundle, _fragment)

    @property
    def applications(self):
        """ Returns list of applications/services
        """
        _applications = []
        for app in self._bundle['applications'].keys():
            _applications.append(self._get_application_fragment(app))
        return _applications

    @property
    def machines(self):
        """ Returns defined machines
        """
        return self._bundle.get('machines', [])

    @property
    def relations(self):
        """ Returns application relations
        """
        return self._bundle.get('relations', [])

    def _get_application_fragment(self, app_name):
        """ Returns bundle fragment
        """
        if app_name not in self._bundle['applications']:
            raise BundleInvalidApplication(
                "Unable find a bundle fragment for: {}".format(app_name))
        _fragment = self._bundle['applications'][app_name]
        return BundleFragment(app_name, _fragment)
