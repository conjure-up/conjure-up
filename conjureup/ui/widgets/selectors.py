from collections.abc import Mapping, Reversible

from urwid import CheckBox, Pile, RadioButton


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


class SelectList(Pile):
    """
    A generic list of selector widgets.

    The type of widgets used as the options must support both a label and a
    value.
    """
    OPTION_TYPE = None

    def __init__(self, opts=None, option_type=None):
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
        self.option_type = option_type or self.OPTION_TYPE
        if self.option_type is None:
            raise TypeError('Must specify an option type')
        if not opts:
            return
        labels = opts.keys() if isinstance(opts, Mapping) else opts
        if not isinstance(labels, Reversible):
            labels = sorted(labels)
        for label in labels:
            value = opts[label] if isinstance(opts, Mapping) else label
            self.append_option(label, value)

    def append_option(self, label, value=None):
        """
        Add an option to the list.

        The option can have a value that is different from the label.
        If no value is given, the label itself will be the value.
        """
        if value is None:
            value = label
        self.append(self._create_option(label, value))

    def _create_option(self, label, value):
        return self.option_type(label, value)

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
    def selected(self):
        """
        Get the values of all selected options.

        Items are filtered by the ``option_type`` of the list.
        """
        return [item[0].value for item in self.contents
                if isinstance(item[0], self.option_type) and item[0].state]


class CheckList(SelectList):
    OPTION_TYPE = ValuedCheckBox


class RadioList(SelectList):
    OPTION_TYPE = ValuedRadioButton

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

    @property
    def value(self):
        if not self.selected:
            return None
        return self.selected[0]


class OptionalRadioList(RadioList):
    OPTION_TYPE = OptionalValuedRadioButton
