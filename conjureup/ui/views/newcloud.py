from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import SelectorHorizontal
from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup.app_config import app


class NewCloudView(WidgetWrap):

    def __init__(self, schema, regions, cb):
        self.schema = schema
        self.regions = regions
        self.regions_w = SelectorHorizontal(self.regions)
        try:
            self.regions_w.set_default(self.schema.default_region, True)
        except NotImplementedError:
            app.log.debug(
                'Attempted to set a default region for cloud({}) '
                'and failed, no default is set in the widget list.'.format(
                    app.current_cloud))
        self.cb = cb
        self.frame = Frame(body=self._build_widget(),
                           footer=self._build_footer())
        self.buttons_selected = False
        super().__init__(self.frame)

    def _gen_credentials(self):
        total_items = [Text(
            "Enter your {} credentials:".format(app.current_cloud.upper()))]
        total_items += [HR()]
        for field in self.schema.fields():
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
        if len(self.regions) > 0:
            total_items.append(
                Columns(
                    [
                        ('weight', 0.5, Text("Select a Cloud Region",
                                             align='right')),
                        self.regions_w
                    ], dividechars=1
                ))
        return total_items

    def _build_widget(self):
        total_items = self._gen_credentials()
        self.pile = Pile(total_items)
        return Padding.center_60(Filler(self.pile, valign="top"))

    def _build_footer(self):
        cancel = menu_btn(on_press=self.cancel,
                          label="\n  BACK\n")
        confirm = menu_btn(on_press=self.submit,
                           label="\n SAVE\n")
        self.buttons = Columns([
            ('fixed', 2, Text("")),
            ('fixed', 13, Color.menu_button(
                cancel,
                focus_map='button_primary focus')),
            Text(""),
            ('fixed', 13, Color.menu_button(
                confirm,
                focus_map='button_primary focus')),
            ('fixed', 2, Text(""))
        ])

        footer = Color.frame_footer(Pile([
            Padding.line_break(""),
            self.buttons
        ]))
        return footer

    def _swap_focus(self):
        if not self.buttons_selected:
            self.buttons_selected = True
            self.frame.focus_position = 'footer'
            self.buttons.focus_position = 3
        else:
            self.buttons_selected = False
            self.frame.focus_position = 'body'

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        rv = super().keypress(size, key)
        return rv

    def cancel(self, btn):
        self.cb(back=True)

    def submit(self, result):
        region = self.regions_w.value
        if self.schema.is_valid():
            self.cb(schema=self.schema,
                    region=region)
