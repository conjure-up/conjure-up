from urwid import ListBox, SimpleListWalker, WidgetWrap


class SimpleList(WidgetWrap):

    def __init__(self, contents, is_selectable=True):
        self.contents = contents
        self.is_selectable = is_selectable
        super().__init__(self._build_widget())

    def _build_widget(self):
        lw = SimpleListWalker([x for x in self.contents])

        return ListBox(lw)

    def selectable(self):
        return self.is_selectable
