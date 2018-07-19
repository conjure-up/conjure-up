""" A View to confirm if user wants to destroy a deployment
"""

from ubuntui.utils import Padding
from urwid import Pile, Text
from conjureup.ui.views.base import BaseView


class DestroyConfirmView(BaseView):
    title = "Confirm Destroy"

    def __init__(self, submit_cb, back_cb):
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        super().__init__()

    def build_widget(self):
        self.message = Text(
            'Are you sure you want to destroy deployment?',
            align='center')
        return Pile([
            Padding.line_break(""),
            self.message,
            Padding.line_break(""),
        ])

    def build_buttons(self):
        return [self.button('YES', self.confirm)]

    def confirm(self):
        self.submit_cb()
