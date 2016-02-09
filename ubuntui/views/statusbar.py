from urwid import WidgetWrap, Text, Pile
from ubuntui.utils import Color


class StatusBarWidget(WidgetWrap):

    """ Displays text in the footers status area."""

    INFO = "[INFO]"
    ERROR = "[ERROR]"
    ARROW = " \u21e8 "

    def __init__(self, text=''):
        self._pending_deploys = Text('')
        self._status_line = Text(text, align="center")
        self._status_extra = self._build_status_extra()
        status = Pile([self._pending_deploys,
                       self._status_extra])
        super().__init__(status)

    def _build_status_extra(self):
        return Color.frame_footer(
            Pile([
                self._status_line
            ]))

    def message(self, text):
        """Write `text` on the footer."""
        self._status_line.set_text(text)

    def error_message(self, text):
        self.message([('status_error', self.ERROR),
                      self.ARROW + text])

    def info_message(self, text):
        self.message([('status_info', self.INFO),
                      self.ARROW + text])

    def set_pending_deploys(self, pending_deploys):
        if len(pending_deploys) > 0:
            msg = "Pending deploys: " + ", ".join(pending_deploys)
            self._pending_deploys.set_text(msg)
        else:
            self._pending_deploys.set_text('')

    def clear(self):
        """Clear the text."""
        self._w.set_text('')
