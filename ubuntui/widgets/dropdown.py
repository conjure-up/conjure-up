import urwid


# class PopUpDialog(urwid.WidgetWrap):
#     """A dialog that appears with nothing but a close button """
#     signals = ['close']
#     def __init__(self):
#         close_button = urwid.Button("that's pretty cool")
#         urwid.connect_signal(close_button, 'click',
#             lambda button:self._emit("close"))
#         pile = urwid.Pile([urwid.Text(
#             "^^  I'm attached to the widget that opened me. "
#             "Try resizing the window!\n"), close_button])
#         fill = urwid.Filler(pile)
#         self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))


class DropDown(urwid.PopUpLauncher):

    def __init__(self, view):
        self.view = view
        super().__init__(self.view)
        urwid.connect_signal(self.original_widget, 'click',
                             lambda button: self.create_pop_up())

    def create_pop_up(self):
        urwid.connect_signal(self.self_view(), 'close',
                             lambda button: self.close_pop_up())

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1,
                'overlay_width': 32, 'overlay_height': 7}
