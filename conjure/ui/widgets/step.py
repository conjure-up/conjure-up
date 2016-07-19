from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import submit_btn
from urwid import (WidgetWrap, Pile, Columns, Text)


class StepWidget(WidgetWrap):
    def __init__(self, app, step_model, step_model_widget, cb):
        """
        Arguments:
        step_model: step model
        step_model_widget: step model widget
        cb: callback
        """
        self.app = app
        self._step_model = step_model
        self._step_model_widget = step_model_widget
        self.cb = cb
        self.step_pile = self.build_widget()
        super().__init__(self.step_pile)

    @property
    def model(self):
        return self._step_model

    @property
    def widget(self):
        return self._step_model_widget

    def __repr__(self):
        return "<StepWidget: {}>".format(self.model.title)

    def set_description(self, description, color='info_minor'):
        self.widget.description.set_text(
            (color, description))

    def set_icon_state(self, result_code):
        """ updates status icon

        Arguments:
        icon: icon widget
        result_code: 3 types of results, error, waiting, complete
        """
        if result_code == "error":
            self.widget.icon.set_text(
                ("error_icon", "\N{BLACK FLAG}"))
        elif result_code == "waiting":
            self.widget.icon.set_text(
                ("pending_icon", "\N{HOURGLASS}"))
        elif result_code == "active":
            self.widget.icon.set_text(
                ("success_icon", "\N{BALLOT BOX WITH CHECK}"))
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            self.widget.icon.set_text(("error_icon", "?"))

    @property
    def current_button_index(self):
        """ Returns the pile index where the button is located
        """
        return len(self.step_pile.contents)-2

    @property
    def current_button_widget(self):
        """ Returns the current button widget
        """
        if self.button:
            return self.button

    def clear_button(self):
        """ Clears current button so it can't be pressed again
        """
        self.app.log.debug(
            "Contents: {}".format(
                self.step_pile.contents[self.current_button_index]))
        self.step_pile.contents[self.current_button_index] = (
            Text(""), self.step_pile.options())

    def build_widget(self):
        return Pile([
            Columns(
                [
                    ('fixed', 3, self.widget.icon),
                    self.widget.description,
                ], dividechars=1
            )]
        )

    def generate_additional_input(self):
        """ Generates additional input fields, useful for doing it after
        a previous step is run
        """
        self.set_description(self.model.description, 'body')
        for i in self.widget.additional_input:
            self.app.log.debug(i)
            self.step_pile.contents.append((Padding.line_break(""),
                                            self.step_pile.options()))
            column_input = [
                ('weight', 0.5, Padding.left(i['label'], left=5))
            ]
            if i['input']:
                column_input.append(
                    ('weight', 1, Color.string_input(
                        i['input'],
                        focus_map='string_input focus')))
            self.step_pile.contents.append(
                (Columns(column_input, dividechars=3),
                 self.step_pile.options()))

            self.button = submit_btn(on_press=self.submit)
            self.step_pile.contents.append(
                (Padding.right_20(
                    Color.button_primary(self.button,
                                         focus_map='button_primary focus')),
                 self.step_pile.options()))
            self.step_pile.contents.append((HR(), self.step_pile.options()))
        self.step_pile.focus_position = self.current_button_index

    def submit(self, btn):
        self.set_icon_state('waiting')
        self.clear_button()
        self.cb(self)
