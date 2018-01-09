from urwid import AttrMap
from ubuntui.widgets.buttons import MenuSelectButton, PlainButton


class StyledButton:
    button_class = PlainButton
    enabled_styles = ('button_primary', 'button_primary focus')
    disabled_styles = ('disabled_button', 'disabled_button focus')

    def __init__(self, label, on_press=None, enabled=True, user_data=None):
        self._button = self.button_class(label, self.on_press)
        self._attrmap = AttrMap(self._button, '')
        self._on_press = on_press
        self.enabled = enabled
        self.user_data = user_data or {}

    def __repr__(self):
        return '<{} "{}">'.format(type(self).__name__, self.label)

    def on_press(self, btn):
        if self.enabled and self._on_press:
            self._on_press(self)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        if self._enabled:
            self.set_attr_map({None: self.enabled_styles[0]})
            self.set_focus_map({None: self.enabled_styles[1]})
        else:
            self.set_attr_map({None: self.disabled_styles[0]})
            self.set_focus_map({None: self.disabled_styles[1]})

    @property
    def base_widget(self):
        # prevent stripping of this class as decoration
        return self

    def __getattr__(self, name):
        """
        Try to pass through unknown attributes to the attrmap,
        and if that fails, try to pass it through to the button.
        """
        if name in ('_original_widget', 'original_widget'):
            # Prevent stripping decoration by blocking access to
            # original_widget.  We have to do this (and block both)
            # because base_widget breaks encapsulation by directly
            # accessing _original_widget.
            raise AttributeError("'{}' object has no attribute '{}'".format(
                type(self).__name__, name))
        try:
            return getattr(self._attrmap, name)
        except AttributeError:
            return getattr(self._button, name)


class FooterButton(StyledButton):
    button_class = MenuSelectButton
    enabled_styles = ('menu_button', 'button_primary focus')
    disabled_styles = ('disabled_button', 'disabled_button_focus')

    def __init__(self, label, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.set_label(label)  # force multi-line
        self._button._label._cursor_position = 1

    def set_label(self, label):
        self._button.set_label('\n  {}\n'.format(label))


class SubmitButton(StyledButton):
    pass


class SecondaryButton(StyledButton):
    enabled_styles = ('button_secondary', 'button_secondary focus')
    disabled_styles = ('disabled_button', 'disabled_button focus')


class ValuedMenuSelectButton(StyledButton):
    button_class = MenuSelectButton
    enabled_styles = ('body', 'menu_button focus')
    disabled_styles = ('info_context', 'disabled_button')

    def __init__(self, label, value, enabled=True, user_data=None):
        self.value = value
        super().__init__(label, None, enabled, user_data)
