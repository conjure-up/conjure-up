from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import Selector
from urwid import (
    BoxAdapter,
    CheckBox,
    Columns,
    Edit,
    Filler,
    Frame,
    Pile,
    RadioButton,
    Text,
    WidgetWrap,
)

from conjureup import events
from conjureup.app_config import app
from conjureup.telemetry import track_screen
from conjureup.ui.widgets.selectors import RadioList

SWAP_FOCUS = 'swap focus'
NEXT_FIELD = 'next field'
PREV_FIELD = 'prev field'
SUBMIT_FIELD = 'submit field'
NEXT_SCREEN = 'next screen'
PREV_SCREEN = 'prev screen'

FORWARD = +1
BACKWARD = -1


class BaseView(WidgetWrap):
    title = 'Base View'
    subtitle = None
    footer = ''
    footer_height = 'auto'
    show_back_button = True

    def __init__(self):
        """Create a new instance of this view.
        """
        self.frame = Frame(body=self._build_body(),
                           footer=self._build_footer())

        self.extend_command_map({
            'control tab': SWAP_FOCUS,
            'tab': NEXT_FIELD,
            'shift tab': PREV_FIELD,
            'enter': SUBMIT_FIELD,
            'meta enter': NEXT_SCREEN,
            'meta right': NEXT_SCREEN,
            'n': NEXT_SCREEN,
            'b': PREV_SCREEN,
            'meta left': PREV_SCREEN,
        })
        self._command_handlers = {
            SWAP_FOCUS: self._swap_focus,
            NEXT_FIELD: self.next_field,
            PREV_FIELD: self.prev_field,
            SUBMIT_FIELD: self.submit_field,
            NEXT_SCREEN: self.submit,
            PREV_SCREEN: self.prev_screen,
        }
        super().__init__(self.frame)

    def extend_command_map(self, command_mappings):
        """
        Extend the command mapping table, which maps keys to command names.

        :param dict command_mappings: A mapping of key names to command names.
            The command names will be looked up in the command handlers table.
            (See :meth:`extend_command_handlers`)  As a convenience,
            ``command_mappings`` can also provide handlers directly instead of
            a command name, in which case a placeholder command name of the
            form ``key: {key name}`` will be created.
        """
        self._command_map = self._command_map.copy()
        for key, command in command_mappings.items():
            if callable(command):
                command_name = 'key: {}'.format(key)
                self._command_map[key] = command_name
                self._command_handlers[command_name] = command
            else:
                self._command_map[key] = command

    def extend_command_handlers(self, command_handlers):
        """
        Extend the command handlers table, which maps command names to
        handler functions.

        :param dict command_handlers: A mapping of command names to the
            functions that are called when that command is invoked.
        """
        self._command_handlers.update(command_handlers)

    def show(self):
        track_screen(self.title)
        app.ui.set_header(title=self.title,
                          excerpt=self.subtitle)
        app.ui.set_body(self)

    @property
    def widget(self):
        """ The widget returned by ``self.build_widget()``.
        """
        return self._widget

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
                Color.menu_button(menu_btn(on_press=lambda btn: callback(),
                                           label="\n  {}\n".format(label)),
                                  focus_map='button_primary focus'))

    def _build_body(self):
        self._widget = self.build_widget()
        if isinstance(self.widget, list):
            self._widget = Pile(self.widget)
        return Pile([
            ('pack', Padding.center_90(HR())),
            Padding.center_80(Filler(self._widget, valign="top")),
        ])

    def set_footer(self, message):
        self.footer_msg.set_text(message)

    def _build_footer(self):
        buttons = []
        buttons.append(('fixed', 2, Text("")))
        buttons.append(self.button('QUIT', events.Shutdown.set))
        if self.show_back_button:
            buttons.append(('fixed', 2, Text("")))
            buttons.append(self.button('BACK', self.prev_screen))
        buttons.append(('weight', 2, Text("")))
        buttons.extend(self.build_buttons())
        buttons.append(('fixed', 2, Text("")))
        self.buttons = Columns(buttons)

        self.footer_msg = Text(self.footer)
        footer_widget = Columns([
            Text(''),
            ('pack', self.footer_msg),
            Text(''),
        ])
        footer_widget = Padding.center_90(self.footer_msg)
        if self.footer_height != 'auto':
            footer_widget = BoxAdapter(Filler(footer_widget, valign='bottom'),
                                       self.footer_height)
        footer = Pile([
            Padding.line_break(""),
            Padding.center_90(HR()),
            Color.body(footer_widget),
            Padding.line_break(""),
            Color.frame_footer(Pile([
                Padding.line_break(""),
                self.buttons,
            ])),
        ])
        return footer

    def prev_screen(self):
        """
        Shut down the current view, and move to the previous screen.

        This should be implemented by a subclass.
        """
        app.log.error('%s: prev_screen not implemented', type(self).__name__)

    def next_screen(self):
        """
        Shut down the current view, and move to the next screen.

        This **must** be implemented by a subclass.
        """
        pass

    def _check_field(self, field):
        """
        Check if a field is acceptable for selecting with :meth:`.next_field`
        or :meth:`.prev_field`.
        """
        if not field.selectable():
            return False
        field = field.base_widget  # strip any decoration
        if isinstance(field, (Edit, CheckBox, Selector, RadioList)):
            # acceptable to the defense, your honor
            return True
        if hasattr(field, 'contents'):
            # recursively check contents of list-type widget
            return any(self._check_field(f[0]) for f in field.contents)
        if hasattr(field, '_w') and field._w is not field:
            # recursively check wrapped widget
            return self._check_field(field._w)
        return False

    def _select_next_field(self, direction):
        if not hasattr(self.widget, 'get_focus_widgets'):
            # top-level widget is not a container, nothing to do
            return False
        focus_path = [self.widget] + self.widget.get_focus_widgets()
        while len(focus_path) > 1:
            # use -2 to get the selected parent of the leaf widget
            container = focus_path[-2]
            if hasattr(container, 'contents'):
                # widget is in fact a container, try to find a field in it
                if direction == FORWARD:
                    start = container.focus_position + 1
                    end = len(container.contents)
                else:
                    start = container.focus_position - 1
                    end = -1  # going backward, range doesn't include end
                for new_position in range(start, end, direction):
                    new_field = container.contents[new_position][0]
                    if not self._check_field(new_field):
                        # not a field we want to select
                        continue
                    container.focus_position = new_position
                    return True
            focus_path.pop()
        else:
            # no more fields
            return False

    def _first_field(self):
        while self._select_next_field(direction=BACKWARD):
            pass

    def _last_field(self):
        while self._select_next_field(direction=FORWARD):
            pass

    def next_field(self, _leave_body=True):
        """
        Find and focus the next non-button selectable.

        :param bool _leave_body: For internal use only.
        :returns: ``True`` if another field was selected, or ``False``.
        """
        if self.frame.focus_position == 'footer':
            self.frame.focus_position = 'body'
            return self._first_field()

        if self._select_next_field(FORWARD):
            return True
        else:
            if _leave_body:
                self._swap_focus()
            return False

    def prev_field(self):
        """
        Find and focus the previous non-button selectable, wrapping from the
        top to the bottom of the body.

        :returns: ``True`` if another field was selected, or ``False``.
        """
        if self.frame.focus_position == 'footer':
            self.frame.focus_position = 'body'
            return self._last_field()

        if self._select_next_field(BACKWARD):
            return True
        else:
            self._swap_focus()
            return False

    def submit_field(self):
        """
        Submit the current field or form.

        By default, this calls ``self.next_field()`` to select the next
        input field, and if there are no more input fields,
        ``self.submit()`` is called.
        """
        if self.frame.focus_position == 'footer':
            # activate selected button
            super().keypress((1, 1), 'enter')
            return
        focused = self.widget.get_focus_widgets()
        if focused:
            field = focused[-1]
            if isinstance(field, RadioButton):
                # activate the selected radio button
                field.keypress(1, 'space')
        if not self.next_field(_leave_body=False):
            self.submit()

    def submit(self):
        """
        Submit the current form.

        By default, this calls ``self.next_screen()`` but most views will
        likely want to do some validation or post-processing, or a given view
        might have more than one form to submit before moving on.  Such views
        should override this method.
        """
        self.next_screen()

    def _swap_focus(self):
        if self.frame.focus_position == 'body':
            self.frame.focus_position = 'footer'
            # select last button
            for i, col in reversed(list(enumerate(self.buttons.contents))):
                if col[0].selectable():
                    self.buttons.focus_position = i
                    break
        else:
            self.frame.focus_position = 'body'

    def keypress(self, size, key):
        command = self._command_map[key]
        if command in self._command_handlers:
            # dispatch via _command_handlers (see __init__)
            result = self._command_handlers[command]()
        else:
            result = super().keypress(size, key)
        self.after_keypress()
        return result

    def after_keypress(self):
        """
        Will be called after a keypress is handled.
        """
        pass


class SchemaFormView(BaseView):
    header = ""

    def __init__(self, submit_cb, back_cb, *args, **kwargs):
        self.submit_cb = submit_cb
        self.back_cb = back_cb
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

    def submit(self):
        if app.provider.is_valid():
            self.submit_cb()

    def prev_screen(self):
        self.back_cb()
