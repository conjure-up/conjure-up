from urwid import WidgetContainerMixin, WidgetWrap


class ContainerWidgetWrap(WidgetWrap, WidgetContainerMixin):
    """
    Base for WidgetWraps that wrap containers and want container methods
    to pass through.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def contents(self):
        return self._w.contents

    @property
    def focus(self):
        return self._w.focus

    @property
    def focus_position(self):
        return self._w.focus_position

    @focus_position.setter
    def focus_position(self, value):
        self._w.focus_position = value
