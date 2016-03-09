""" Horizontal rule widget
"""

from __future__ import unicode_literals
from urwid import Divider
from functools import partial
from ubuntui.utils import Color


# Show the user this view can be scrolled
HR = partial(Color.divider_line,
             Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
