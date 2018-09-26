import asyncio
import random
import unicodedata
from pathlib import Path

from ubuntui.utils import Padding
from urwid import Columns, Text

from conjureup import events
from conjureup.app_config import app
from conjureup.ui.views.base import BaseView


class InterstitialView(BaseView):
    body_valign = 'middle'
    icons = [('pending_icon', "\u2581"),
             ('pending_icon', "\u2582"),
             ('pending_icon', "\u2583"),
             ('pending_icon', "\u2584"),
             ('pending_icon', "\u2585"),
             ('pending_icon', "\u2586"),
             ('pending_icon', "\u2587"),
             ('pending_icon', "\u2588")]

    def __init__(self, title, message, event, watch_file=None):
        self.title = title
        self.message = message
        self.event = event
        self.watch_file = Path(watch_file) if watch_file else None
        self.output = Text("", align="left")
        self.loading_boxes = [Text(x) for x in self.icons]
        super().__init__()
        app.loop.create_task(self._refresh())

    def build_widget(self):
        """ creates a loading screen if nodes do not exist yet """
        body = [Padding.line_break(""),
                Text(self.message, align="center"),
                Padding.line_break(""),
                Padding.center_90(self.output),
                Padding.line_break("")]

        _boxes = [('weight', 1, Text(''))]
        for i in self.loading_boxes:
            _boxes.append(('pack', i))
        _boxes.append(('weight', 1, Text('')))
        body.append(Columns(_boxes))

        return body

    def _clear_control_characters(self, text):
        text = text.decode().splitlines()
        new_out = []
        for t in text:
            sanitize = "".join(ch for ch
                               in t if unicodedata.category(ch)[0] != "C")
            if sanitize.endswith("%"):
                new_out.append("{}%".format(sanitize.split("%")[0]))
            else:
                new_out.append(sanitize[:134])
        if len(new_out) >= 10:
            return "\n".join(new_out[-10:])
        else:
            return "\n".join(new_out)

    async def _refresh(self):
        while self.event.is_set() and not events.Error.is_set():
            self.update()
            await asyncio.sleep(1)

    def update(self):
        """ Redraws the KITT bar, and updates the watch file output.
        """
        random.shuffle(self.icons)
        for i in self.loading_boxes:
            i.set_text(self.icons[random.randrange(len(self.icons))])

        if self.watch_file:
            try:
                text = self.watch_file.read_text().splitlines()[-10:]
                text = self._clear_control_characters(text)
            except Exception:
                text = "Waiting..."
            self.output.set_text(text)
