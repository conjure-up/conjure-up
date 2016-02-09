""" Descriptor widgets
"""

from __future__ import unicode_literals
from urwid import Text
from functools import partial


# Show the user this view can be scrolled
MetaScroll = partial(Text, "(\u21C5 Scroll)")
