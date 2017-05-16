from ubuntui.utils import Color
from ubuntui.widgets.buttons import menu_btn
from urwid import Pile, WidgetWrap


class SelectorList(WidgetWrap):
    def __init__(self, choices, on_select):
        self._pile = Pile([])
        self.on_select = on_select
        for choice in choices:
            self.add_choice(choice)
        super().__init__(self._pile)

    def add_choice(self, choice):
        self._pile.contents.append((
            Color.body(
                menu_btn(label=choice,
                         on_press=self._select),
                focus_map='menu_button focus'
            ), self._pile.options()))

    def _select(self, item):
        self.on_select(item.label)
