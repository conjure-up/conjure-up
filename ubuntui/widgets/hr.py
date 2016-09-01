""" Horizontal rule widget
"""

from __future__ import unicode_literals
from urwid import Divider
from ubuntui.utils import Color


# Show the user this view can be scrolled
def HR(top=1, bottom=1):
    """ Returns a horiztonal divider

    Arguments:
    top: padding top
    bottom: padding bottom
    """
    return Color.divider_line(
        Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", top, bottom))
