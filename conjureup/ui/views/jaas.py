from urwid import Columns, Edit, Filler, Frame, Pile, Text, WidgetWrap

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn, submit_btn


class JaaSLoginView(WidgetWrap):

    def __init__(self, app, error=None, cb=None):
        self.app = app
        self.error = error
        self.cb = cb
        self.config = self.app.config
        self.buttons_pile_selected = False
        self.fields = None
        self.frame = Frame(body=self._build_widget(),
                           footer=self._build_footer())
        self.tab_order = [
            'email',
            'password',
            'twofa',
            'login',
            'quit',
        ]
        self.focus_by_fields = {
            'email': ('body', 0, None),
            'password': ('body', 2, None),
            'twofa': ('body', 4, None),
            'login': ('body', 6, 0),
            'browser': ('body', 6, 2),
            'quit': ('footer', None, None),
        }
        super().__init__(self.frame)

    def _build_widget(self):
        email = Edit()
        password = Edit(mask='*')
        twofa = Edit()
        # can't use IntEdit because it precludes leading zeros
        twofa.valid_char = lambda ch: ch in '0123456789'
        labels = Pile([Text("Email:"),
                       Padding.line_break(""),
                       Text("Password:"),
                       Padding.line_break(""),
                       Text("Two-Factor Auth (2FA):")])
        buttons = Columns([
            (9, Color.menu_button(
                submit_btn(
                    label="Login",
                    on_press=lambda btn: self.cb(
                        email.edit_text,
                        password.edit_text,
                        twofa.edit_text)
                ), focus_map='button_primary focus')),
            # (2, Text("")),
            # (21, Color.menu_button(
            #     submit_btn(
            #         label="Login via Browser",
            #     ), focus_map='button_primary focus')),
        ])
        fields = Pile([Color.string_input(email),
                       Padding.line_break(""),
                       Color.string_input(password),
                       Padding.line_break(""),
                       Color.string_input(twofa),
                       Padding.line_break(""),
                       buttons])
        self.fields = fields
        self.buttons = buttons

        rows = [Columns([(23, labels), fields])]
        if self.error:
            rows.extend([
                Padding.line_break(""),
                Color.error_major(Text(" {}".format(self.error))),
            ])
        return Padding.center_60(Filler(Pile(rows), valign='top'))

    def _build_footer(self):
        footer_pile = Pile([
            Padding.center_60(Text(
                'Enter your Ubuntu SSO (Launchpad) email address and '
                'password.  If you have Two-Factor Authentication (2FA) '
                'enabled, enter that as well, otherwise leave that field '
                'blank.  For more information about 2FA, see: '
                'https://help.ubuntu.com/community/SSO/FAQs/2FA'
            )),
            Padding.line_break(""),
            Color.frame_footer(
                Columns([
                    ('fixed', 2, Text("")),
                    ('fixed', 13, self._build_buttons())
                ]))
        ])
        return footer_pile

    def _build_buttons(self):
        cancel = menu_btn(on_press=self.cancel,
                          label="\n  QUIT\n")
        buttons = [
            Padding.line_break(""),
            Color.menu_button(cancel,
                              focus_map='button_primary focus'),
        ]
        self.buttons_pile = Pile(buttons)
        return self.buttons_pile

    def _find_tab_index(self):
        for tab_index, field in enumerate(self.tab_order):
            frame, fields, button = self.focus_by_fields[field]
            if all([
                frame == self.frame.focus_position,
                fields in (None, self.fields.focus_position),
                button in (None, self.buttons.focus_position),
            ]):
                return tab_index
        else:
            return None

    def _update_focus(self, field):
        frame_focus, field_focus, button_focus = self.focus_by_fields[field]
        self.frame.focus_position = frame_focus
        if field_focus is not None:
            self.fields.focus_position = field_focus
        if button_focus is not None:
            self.buttons.focus_position = button_focus

    def _inc_focus(self):
        tab_index = self._find_tab_index()
        new_focus = self.tab_order[(tab_index + 1) % len(self.tab_order)]
        self._update_focus(new_focus)

    def _dec_focus(self):
        tab_index = self._find_tab_index()
        new_focus = self.tab_order[(tab_index - 1) % len(self.tab_order)]
        self._update_focus(new_focus)

    def keypress(self, size, key):
        tab_index = self._find_tab_index()

        if tab_index is None:
            self.app.log.error('Unknown tab index')
            return super().keypress(size, key)

        if key in ('tab', 'shift tab', 'enter'):
            if key == 'tab':
                return self._inc_focus()
            elif key == 'shift tab':
                return self._dec_focus()
            elif key == 'enter':
                if tab_index < 2:
                    return self._inc_focus()
                elif tab_index == 2:
                    self._update_focus('login')
                    return super().keypress(size, 'enter')
                else:
                    return super().keypress(size, 'enter')
        else:
            return super().keypress(size, key)

    def cancel(self, btn):
        EventLoop.exit(0)
