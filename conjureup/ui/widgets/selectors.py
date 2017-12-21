from collections.abc import Mapping, Reversible

from urwid import AttrMap, CheckBox, Pile, RadioButton
from ubuntui.widgets.buttons import MenuSelectButton


class ValuedCheckBox(CheckBox):
    """
    Subclass of CheckBox that associates a value with the checkbox.
    """

    def __init__(self, label, value, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.value = value


class ValuedRadioButton(RadioButton):
    """
    Subclass of RadioButton that associates a value with the radio button.
    """

    def __init__(self, group, label, value, *args, **kwargs):
        super().__init__(group, label, *args, **kwargs)
        self.value = value


class OptionalValuedRadioButton(ValuedRadioButton):
    """
    Subclass of ValuedRadioButton that supports deselection.
    """

    def __init__(self, group, label, value, state=False, *args, **kwargs):
        super().__init__(group, label, value, state, *args, **kwargs)

    def toggle_state(self):
        if self.state is False:
            self.set_state(True)
        elif self.state is True:
            self.set_state(False)


class ValuedMenuSelectButton(AttrMap):
    def __init__(self, label, value, enabled=True, user_data=None):
        super().__init__(MenuSelectButton(label), '')
        self.value = value
        self.enabled = enabled
        self.user_data = user_data or {}

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        if self._enabled:
            self.set_attr_map({None: 'body'})
            self.set_focus_map({None: 'menu_button focus'})
        else:
            self.set_attr_map({None: 'info_context'})
            self.set_focus_map({None: 'disabled_button'})


class SelectList(Pile):
    """
    A generic list of selector widgets.

    The type of widgets used as the options must support both a label and a
    value.
    """
    option_type = None
    allow_multiple = True
    wrapable = False

    def __init__(self, opts=None, option_type=None, allow_multiple=None,
                 wrapable=None):
        """
        Create a new list.

        :param opts: Optional sequence or mapping containing the initial set
            of items to select from. If a sequence is provided, the items will
            be used as both the labels and the values for the items. If a
            mapping is provided, the keys will be considered the labels and
            the values the values.  If the mapping is an ``OrderedDict``,
            the order will be preserved.  Otherwise, the items will be sorted
            by the labels (keys).
        """
        super().__init__([])
        self.option_type = option_type or self.option_type
        if self.option_type is None:
            raise TypeError('Must specify an option type')
        if allow_multiple is not None:
            self.allow_multiple = allow_multiple
        if wrapable is not None:
            self.wrapable = wrapable
        if not opts:
            return
        labels = opts.keys() if isinstance(opts, Mapping) else opts
        if not isinstance(labels, Reversible):
            labels = sorted(labels)
        for label in labels:
            value = opts[label] if isinstance(opts, Mapping) else label
            self.append_option(label, value)

    def append_option(self, label, value=..., **kwargs):
        """
        Add an option to the list.

        The option can have a value that is different from the label.
        If no value is given, the label itself will be the value.
        """
        if value is ...:
            value = label
        self.append(self._create_option(label, value, **kwargs))

    def _create_option(self, label, value, **kwargs):
        return self.option_type(label, value, **kwargs)

    def append(self, widget, height_type='weight', height_amount=1):
        """
        Add a child widget to the list.

        :param widget: A child widget.
        :param height_type: ``'pack'``, ``'given'`` or ``'weight'``
        :param height_amount: ``None`` for ``'pack'``, a number of rows for
            ``'fixed'`` or a weight value (number) for ``'weight'``
        """
        self.contents.append((widget, self.options(height_type,
                                                   height_amount)))

    @property
    def option_widgets(self):
        """
        List of all child widgets that are instances of ``self.option_type``.
        """
        return [item[0] for item in self.contents
                if isinstance(item[0], self.option_type)]

    @property
    def selected(self):
        """
        Get the values of all selected option items.
        """
        if not hasattr(self.option_widgets[0], 'state'):
            if getattr(self.focus, 'enabled', True):
                return self.focus.value
            else:
                return None
        else:
            selected = [option.value for option in self.option_widgets
                        if option.state and getattr(option, 'enabled', True)]
            if self.allow_multiple:
                return selected
            else:
                return selected[0] if selected else None

    @property
    def value(self):
        """
        Alias for :meth:`.selected`.
        """
        return self.selected

    def _move_limit(self, bottom=True):
        indexes = range(len(self.contents))
        if bottom:
            indexes = reversed(indexes)
        for index in indexes:
            if self.contents[index][0].selectable():
                self.focus_position = index
                break

    def keypress(self, size, key):
        if not self.wrapable or key not in ('up', 'down', 'home', 'end'):
            return super().keypress(size, key)
        if key in ('up', 'down'):
            # do the normal thing, and if successful, return
            new_key = super().keypress(size, key)
            if new_key is None:
                return  # handled by base
        if key in ('up', 'end'):
            # wrap from top, or press end
            self._move_limit(bottom=True)
        if key in ('down', 'home'):
            # wrap from bottom, or press home
            self._move_limit(bottom=False)

    def select_item(self, index):
        item = self.option_widgets[index]
        if hasattr(item, 'set_state'):
            item.set_state(True)
        else:
            real_index = [i for i in range(len(self.contents))
                          if self.contents[i][0] is item][0]
            self.focus_position = real_index

    def select_item_by_value(self, value):
        opts = self.option_widgets
        for i, opt in enumerate(opts):
            if opt.value == value:
                self.select_item(i)
                break

    def select_first(self):
        opts = self.option_widgets
        for i, opt in enumerate(opts):
            if getattr(opt, 'enabled', True):
                self.select_item(i)
                break


class CheckList(SelectList):
    option_type = ValuedCheckBox


class RadioList(SelectList):
    option_type = ValuedRadioButton
    allow_multiple = False

    def __init__(self, *args, **kwargs):
        self.group = []
        super().__init__(*args, **kwargs)

    def _create_option(self, label, value):
        return self.option_type(self.group, label, value)

    def select_first_option(self):
        """
        Select the first option.
        """
        for item in self.contents:
            if isinstance(item, self.option_type):
                item.set_state(True)
                break

    def select_option(self, value):
        """
        Select an option by value.
        """
        for item in self.contents:
            if isinstance(item, self.option_type):
                item.set_state(item.value == value)


class OptionalRadioList(RadioList):
    option_type = OptionalValuedRadioButton


class MenuSelectButtonList(SelectList):
    option_type = ValuedMenuSelectButton
    wrapable = True

    def __init__(self, opts=None, default=None, *args, **kwargs):
        super().__init__(opts, *args, **kwargs)
        if default:
            self.select_item_by_value(default)
        else:
            self.select_first()
