from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR
from urwid import Columns, ListBox, Text, WidgetWrap


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
        super().__init__(ListBox(self.result_pile))

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
            from conjureup.app_config import app
            app.log.debug('Rendering result: {} -> {}'.format(k, v))
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
