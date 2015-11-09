# Copyright 2015 Canonical Ltd.

""" Re-usable input widgets
"""

from urwid import (Edit, IntEdit, RadioButton, WidgetWrap)
import logging
import re

log = logging.getLogger("widgets.input")


class StringEditor(WidgetWrap):
    """ Edit input class
    Initializes and Edit object and attachs its result
    to the `value` accessor.
    """
    def __init__(self, caption, **kwargs):
        self._edit = Edit(caption=caption, **kwargs)
        self.error = None
        super().__init__(self._edit)

    def keypress(self, size, key):
        if self.error:
            self._edit.set_edit_text("")
            self.error = None
        return super().keypress(size, key)

    def set_error(self, msg):
        self.error = msg
        return self._edit.set_edit_text(msg)

    @property
    def value(self):
        return self._edit.get_edit_text()

    @value.setter  # NOQA
    def value(self, value):
        self._edit.set_edit_text(value)


class PasswordEditor(StringEditor):
    """ Password input prompt with masking
    """
    def __init__(self, caption, mask="*"):
        super().__init__(caption, mask=mask)


class RealnameEditor(StringEditor):
    """ Username input prompt with input rules
    """

    def keypress(self, size, key):
        ''' restrict what chars we allow for username '''

        realname = r'[a-zA-Z0-9_\- ]'
        if re.match(realname, key) is None:
            return False

        return super().keypress(size, key)


class UsernameEditor(StringEditor):
    """ Username input prompt with input rules
    """

    def keypress(self, size, key):
        ''' restrict what chars we allow for username '''

        userlen = len(self.value)
        if userlen == 0:
            username = r'[a-z_]'
        else:
            username = r'[a-z0-9_-]'

        # don't allow non username chars
        if re.match(username, key) is None:
            return False

        return super().keypress(size, key)


class MountEditor(StringEditor):
    """ Mountpoint input prompt with input rules
    """

    def keypress(self, size, key):
        ''' restrict what chars we allow for mountpoints '''

        mountpoint = r'[a-zA-Z0-9_/\.\-]'
        if re.match(mountpoint, key) is None:
            return False

        return super().keypress(size, key)


class IntegerEditor(WidgetWrap):
    """ IntEdit input class
    """
    def __init__(self, caption, default=0):
        self._edit = IntEdit(caption=caption, default=default)
        super().__init__(self._edit)

    @property
    def value(self):
        return self._edit.get_edit_text()


class Selector(WidgetWrap):
    """ Radio selection list of options
    """
    def __init__(self, opts):
        """
        :param list opts: list of options to display
        """
        self.opts = opts
        self.group = []
        self._add_options()

    def _add_options(self):
        for item in self.opts:
            RadioButton(self.group, item)

    @property
    def value(self):
        for item in self.group:
            log.debug(item)
            if item.get_state():
                return item.label
        return "Unknown option"


class YesNo(Selector):
    """ Yes/No selector
    """
    def __init__(self):
        opts = ['Yes', 'No']
        super().__init__(opts)
