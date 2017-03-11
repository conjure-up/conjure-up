import datetime

from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.api.models import model_status
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.text import Instruction


class DestroyConfirmView(WidgetWrap):

    def __init__(self, app, controller, model, cb):
        self.app = app
        self.cb = cb
        self.controller = controller
        self.model = model
        self.config = self.app.config
        self.buttons_pile_selected = False
        self.frame = Frame(body=self._build_widget(),
                           footer=self._build_footer())

        self.frame.focus_position = 'footer'
        self.buttons.focus_position = 1

        super().__init__(self.frame)

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def _swap_focus(self):
        if not self.buttons_pile_selected:
            self.buttons_pile_selected = True
            self.frame.focus_position = 'footer'
            self.buttons.focus_position = 1
        else:
            self.buttons_pile_selected = False
            self.frame.focus_position = 'body'

    def _build_footer(self):
        no = menu_btn(on_press=self.cancel,
                      label="\n  NO\n")
        yes = menu_btn(on_press=self.submit,
                       label="\n  YES\n")
        self.buttons = Columns([
            ('fixed', 2, Text("")),
            ('fixed', 11, Color.menu_button(
                no,
                focus_map='button_primary focus')),
            Text(""),
            ('fixed', 11, Color.menu_button(
                yes,
                focus_map='button_primary focus')),
            ('fixed', 2, Text(""))
        ])

        self.footer = Pile([
            Padding.line_break(""),
            self.buttons
        ])
        return Color.frame_footer(self.footer)

    def _sanitize_date(self, date_obj):
        """ Some cases juju uses human readable date/time like X secs ago and models
        that run longer get a typical datetime.date object, need to make sure
        of which one we're dealing with

        Arguments:
        date_obj: datetime.date object

        Returns:
        String representation of date or the Juju human readable string
        if applicable
        """
        if isinstance(date_obj, datetime.date):
            return date_obj.strftime('%Y-%m-%d')
        else:
            return str(date_obj)

    def _total_machines(self, model):
        """ Returns total machines in model
        """
        machines = model.get('machines', None)
        if machines is None:
            return 0
        return len(machines.keys())

    def _build_widget(self):
        applications = model_status().applications
        total_items = []
        total_items.append(Instruction("Deployment Information:"))
        total_items.append(HR())
        tbl = Pile([
            Columns([('fixed', 15, Text("Name")),
                     Text(self.model['name'])]),
            Columns([('fixed', 15, Text("Cloud")),
                     Text(self.model['cloud'])]),
            Columns([('fixed', 15, Text("Status")),
                     Text(self.model['status']['current'])]),
            Columns([('fixed', 15, Text("Online")),
                     Text(self._sanitize_date(
                         self.model['status']['since']))]),
            Columns([('fixed', 15, Text("Applications")),
                     Text(", ".join(applications.keys()))]),
            Columns([('fixed', 15, Text("Machines")),
                     Text(str(self._total_machines(self.model)))])

        ])
        total_items.append(tbl)
        total_items.append(HR())
        return Padding.center_80(Filler(Pile(total_items), valign='top'))

    def submit(self, btn):
        self.footer.contents[-1] = (Text(""), self.footer.options())
        self.cb(self.controller, self.model['name'])

    def cancel(self, btn):
        self.cb(None, None)
