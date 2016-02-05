# Copyright 2015-2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
