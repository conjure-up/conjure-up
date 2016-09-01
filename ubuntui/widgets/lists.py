from urwid import ListBox, SimpleListWalker


class SimpleList(ListBox):

    def __init__(self, contents, is_selectable=True):
        self.contents = contents
        self.is_selectable = is_selectable
        self.lbox = self._build_widget()
        super().__init__(self.lbox)

    def _build_widget(self):
        lw = SimpleListWalker([x for x in self.contents])

        return lw

    def selectable(self):
        return self.is_selectable
