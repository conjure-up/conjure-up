from urwid import Columns, Edit, Filler, Frame, Pile, Text, WidgetWrap

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn


class JaaSLoginView(WidgetWrap):

    def __init__(self, app, error=None, cb=None):
        self.app = app
        self.error = error
        self.cb = cb
        self.config = self.app.config
        self.field_labels = self._build_field_labels()
        self.fields = self._build_fields()
        self.buttons = self._build_buttons()
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
            'email': ('body', 0),
            'password': ('body', 2),
            'twofa': ('body', 4),
            'login': ('footer', 3),
            'quit': ('footer', 1),
        }
        super().__init__(self.frame)

    def _build_field_labels(self):
        return Pile([Text("Email:"),
                     Padding.line_break(""),
                     Text("Password:"),
                     Padding.line_break(""),
                     Text("Two-Factor Auth (2FA):")])

    def _build_fields(self):
        self.email = Edit()
        self.password = Edit(mask='*')
        self.twofa = Edit()
        # can't use IntEdit because it precludes leading zeros
        self.twofa.valid_char = lambda ch: ch in '0123456789'

        return Pile([Color.string_input(self.email),
                     Padding.line_break(""),
                     Color.string_input(self.password),
                     Padding.line_break(""),
                     Color.string_input(self.twofa)])

    def _build_buttons(self):
        return Columns([
            ('fixed', 2, Text("")),
            ('fixed', 13, Color.menu_button(menu_btn(on_press=self.cancel,
                                                     label="\n  QUIT\n"),
                                            focus_map='button_primary focus')),
            Text(""),
            ('fixed', 13, Color.menu_button(menu_btn(on_press=self.login,
                                                     label="\n  LOGIN\n"),
                                            focus_map='button_primary focus')),
            ('fixed', 2, Text("")),
        ])

    def _build_widget(self):
        rows = [
            Columns([('fixed', 23, self.field_labels), self.fields]),
        ]
        if self.error:
            rows.extend([
                Padding.line_break(""),
                Color.error_major(Text(" {}".format(self.error))),
            ])
        return Padding.center_60(Filler(Pile(rows), valign='top'))

    def _build_footer(self):
        return Pile([
            Padding.center_60(Text(
                'Enter your Ubuntu SSO (Launchpad) email address and '
                'password.  If you have Two-Factor Authentication (2FA) '
                'enabled, enter that as well, otherwise leave that field '
                'blank.  For more information about 2FA, see: '
                'https://help.ubuntu.com/community/SSO/FAQs/2FA'
            )),
            Padding.line_break(""),
            Color.frame_footer(Pile([
                Padding.line_break(""),
                self.buttons,
            ])),
        ])

    def _find_tab_index(self):
        for tab_index, field in enumerate(self.tab_order):
            frame_focus, widget_focus = self.focus_by_fields[field]
            if all([
                frame_focus == self.frame.focus_position,
                widget_focus == (self.fields.focus_position
                                 if frame_focus == 'body' else
                                 self.buttons.focus_position),
            ]):
                return tab_index
        else:
            return None

    def _focus_field(self, field):
        frame_focus, widget_focus = self.focus_by_fields[field]
        self.frame.focus_position = frame_focus
        if frame_focus == 'body':
            self.fields.focus_position = widget_focus
        else:
            self.buttons.focus_position = widget_focus

    def _inc_focus(self):
        tab_index = self._find_tab_index()
        field_to_focus = self.tab_order[(tab_index + 1) % len(self.tab_order)]
        self._focus_field(field_to_focus)

    def _dec_focus(self):
        tab_index = self._find_tab_index()
        field_to_focus = self.tab_order[(tab_index - 1) % len(self.tab_order)]
        self._focus_field(field_to_focus)

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
                    self._focus_field('login')
                    return super().keypress(size, 'enter')
                else:
                    return super().keypress(size, 'enter')
        else:
            return super().keypress(size, key)

    def login(self, btn):
        self.cb(self.email.edit_text,
                self.password.edit_text,
                self.twofa.edit_text)

    def cancel(self, btn):
        EventLoop.exit(0)
