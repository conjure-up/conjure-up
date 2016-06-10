from __future__ import unicode_literals
from urwid import Button, Text
from functools import partial


class PlainButton(Button):
    button_left = Text("[")
    button_right = Text("]")


class MenuSelectButton(Button):
    button_left = Text("")
    button_right = Text("")


confirm_btn = partial(PlainButton, label="Confirm", on_press=None)
submit_btn = partial(PlainButton, label="Submit", on_press=None)
cancel_btn = partial(PlainButton, label="Cancel", on_press=None)
back_btn = partial(PlainButton, label="Back", on_press=None)
quit_btn = partial(PlainButton, label="Quit", on_press=None)
done_btn = partial(PlainButton, label="Done", on_press=None)
reset_btn = partial(PlainButton, label="Reset", on_press=None)
menu_btn = partial(MenuSelectButton, on_press=None)
select_btn = partial(MenuSelectButton,
                     label="Select \u2193",
                     on_press=None)
