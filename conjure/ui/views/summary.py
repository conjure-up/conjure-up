from ubuntui.utils import Padding
from urwid import WidgetWrap, Text, Filler, Pile, Columns
from ubuntui.widgets.hr import HR


class SummaryView(WidgetWrap):

    def __init__(self, app, results, cb):
        self.app = app
        self.results = results
        self.cb = cb
        self.result_pile = [
            Padding.line_break("")
        ]
        self.result_pile += [Padding.center_90(s)
                             for s in self.build_results()]
        super().__init__(Filler(Pile(self.result_pile), valign="top"))

    def build_results(self):
        rows = []
        rows.append(
            Columns([
                ('weight', 0.1, Text('Application')),
                ('weight', 0.4, Text('Result'))
            ], dividechars=5
            )
        )
        rows.append(HR())
        rows.append(Padding.line_break(""))
        for k, v in self.results.items():
            rows.append(
                    Columns(
                        [
                            ('weight', 0.1, Text(k)),
                            ('weight', 0.4, Text(v))
                        ], dividechars=5
                    )
            )
            self.app.log.debug(rows)
        return rows
