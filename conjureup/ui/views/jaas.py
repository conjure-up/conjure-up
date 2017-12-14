from ubuntui.utils import Color, Padding
from urwid import Columns, Edit, Text

from conjureup.ui.views.base import BaseView


class JaaSLoginView(BaseView):
    title = 'Login to JaaS'
    subtitle = 'Enter your Ubuntu SSO credentials'
    footer = ('Enter your Ubuntu SSO (Launchpad) email address and '
              'password.  If you have Two-Factor Authentication (2FA) '
              'enabled, enter that as well, otherwise leave that field '
              'blank.  For more information about 2FA, see: '
              'https://help.ubuntu.com/community/SSO/FAQs/2FA')

    def __init__(self, submit_cb, back_cb, error=None):
        self.submit_cb = submit_cb
        self.prev_screen = back_cb
        self.error = error

        self.email = Edit()
        self.password = Edit(mask='*')
        self.twofa = Edit()
        # can't use IntEdit because it precludes leading zeros
        self.twofa.valid_char = lambda ch: ch in '0123456789'

        super().__init__()

    def build_widget(self):
        rows = []

        def add_row(label, field):
            rows.extend([
                Columns([('fixed', 23, Text(label)),
                         Color.string_input(field,
                                            focus_map='string_input focus')]),
                Padding.line_break(""),
            ])

        add_row('Email:', self.email),
        add_row('Password:', self.password),
        add_row('Two-Factor Auth (2FA):', self.twofa),
        if self.error:
            rows.append(Color.error_major(Text(" {}".format(self.error))))
        return rows

    def build_buttons(self):
        return [self.button('LOGIN', self.submit)]

    def submit(self):
        self.submit_cb(self.email.edit_text,
                       self.password.edit_text,
                       self.twofa.edit_text)
