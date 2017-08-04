from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup import events
from conjureup.app_config import app
from conjureup.telemetry import track_screen


class BaseView(WidgetWrap):
    title = 'Base View'
    subtitle = None
    footer = ''

    def __init__(self, back=None):
        """Create a new instance of this view.

        :param back: Callback to invoke when the BACK button is selected.
            If None, the BACK button will be hidden.
        """
        self.back = back
        self.frame = Frame(body=self._build_body(),
                           footer=self._build_footer())
        self.buttons_selected = False
        super().__init__(self.frame)

    def show(self):
        track_screen(self.title)
        app.ui.set_header(title=self.title,
                          excerpt=self.subtitle)
        app.ui.set_body(self)
        app.ui.set_footer(self.footer)

    def build_widget(self):
        """ Build the main widget(s) for the view.

        Return a widget, or a list of widgets to be rendered in a Pile,
        which will be used as the main body of the view.

        This **must** be implemented by a subclass.
        """
        raise NotImplementedError()

    def build_buttons(self):
        """ Build any buttons for the footer.

        Should call `self.button(label, callback)` to construct each button,
        and return a list of such buttons.
        """
        return []

    def button(self, label, callback):
        """ Build a button for the footer with the given label and callback.

        """
        return ('fixed', len(label) + 8,
                Color.menu_button(menu_btn(on_press=callback,
                                           label="\n  {}\n".format(label)),
                                  focus_map='button_primary focus'))

    def _build_body(self):
        widget = self.build_widget()
        if isinstance(widget, list):
            widget = Pile(widget)
        return Padding.center_80(Filler(widget, valign="top"))

    def _build_footer(self):
        buttons = []
        buttons.append(('fixed', 2, Text("")))
        if self.back:
            buttons.append(self.button('BACK',
                                       lambda btn: self.back()))
        else:
            buttons.append(self.button('QUIT',
                                       lambda btn: events.Shutdown.set()))
        buttons.append(('weight', 2, Text("")))
        buttons.extend(self.build_buttons())
        buttons.append(('fixed', 2, Text("")))
        self.buttons = Columns(buttons)

        footer = Color.frame_footer(Pile([
            Padding.line_break(""),
            self.buttons
        ]))
        return footer

    def _swap_focus(self):
        if not self.buttons_selected:
            self.buttons_selected = True
            self.frame.focus_position = 'footer'
            num_buttons = len(self.buttons.contents) - 3  # 3 spacers
            if num_buttons > 1:
                self.buttons.focus_position = num_buttons + 1  # last button
            else:
                self.buttons.focus_position = 1  # QUIT / BACK
        else:
            self.buttons_selected = False
            self.frame.focus_position = 'body'

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        rv = super().keypress(size, key)
        return rv


class SchemaFormView(BaseView):
    header = ""

    def __init__(self, submit_cb, *args, **kwargs):
        self.submit_cb = submit_cb
        super().__init__(*args, **kwargs)

    def build_widget(self):
        total_items = []
        if self.header:
            total_items.extend([
                Text(self.header),
                HR(),
            ])
        for field in app.provider.form.fields():
            label = field.key
            if field.label is not None:
                label = field.label

            col = Columns(
                [
                    ('weight', 0.5, Text(label, align='right')),
                    Color.string_input(
                        field.widget,
                        focus_map='string_input focus')
                ], dividechars=1
            )
            total_items.append(col)
            total_items.append(
                Columns(
                    [
                        ('weight', 0.5, Text("")),
                        Color.error_major(field.error)
                    ], dividechars=1
                )
            )
            total_items.append(Padding.line_break(""))
        return total_items

    def build_buttons(self):
        return [self.button('SAVE', self.submit)]

    def submit(self, result):
        if app.provider.is_valid():
            self.submit_cb()
