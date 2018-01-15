from urwid import (
    CanvasCombine,
    CanvasJoin,
    CompositeCanvas,
    Filler,
    SolidCanvas,
    WidgetContainerMixin,
    WidgetWrap
)


class ContainerWidgetWrap(WidgetWrap, WidgetContainerMixin):
    """
    Base for WidgetWraps that wrap containers and want container methods
    to pass through.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def contents(self):
        return self._w.contents

    @property
    def focus(self):
        return self._w.focus

    @property
    def focus_position(self):
        return self._w.focus_position

    @focus_position.setter
    def focus_position(self, value):
        self._w.focus_position = value


class Scrollable(Filler):
    """
    Modified Filler that supports scrolling long contents.
    """
    thumb_char = '\u2588'
    trough_char = '\u2502'

    @property
    def scroll_top(self):
        return getattr(self, '_scroll_top', 0)

    @scroll_top.setter
    def scroll_top(self, value):
        """
        The current scroll position from the top of the widget.

        This many lines will be trimmed from the top of the widget.
        """
        self._scroll_top = max(value, 0)
        self._invalidate()  # invalidate render cache

    def render(self, size, focus):
        maxcols, maxrows = size
        rows = self._original_widget.rows((maxcols,), focus)
        if rows <= maxrows:
            # no clipping, so just fill as normal
            return super().render(size, focus)

        # limit scroll_top to top of last page
        self.scroll_top = min(self.scroll_top, rows - maxrows)

        ocanv = self._original_widget.render((maxcols,), focus)
        if ocanv.cursor is not None:
            # ensure selected field is within scroll window
            cx, cy = ocanv.cursor
            if self.scroll_top <= cy < self.scroll_top + maxrows:
                pass  # already in view
            elif cy < maxrows / 2:
                self.scroll_top = 0
            elif cy > rows - maxrows / 2:
                self.scroll_top = rows - maxrows
            else:
                self.scroll_top = int(cy - maxrows / 2)

        # calculate top / bottom values for pad_trim_top_bottom
        top = -self.scroll_top
        bottom = -(rows - self.scroll_top - maxrows)

        canv = CompositeCanvas(ocanv)
        canv.pad_trim_top_bottom(top, bottom)

        if rows != 0:
            # calculate top and bottom of scroll thumb as percentage of maxrows
            sf = maxrows / rows
            thumb_top = int(self.scroll_top * sf)
            thumb_bottom = int((rows - (self.scroll_top + maxrows)) * sf)
            thumb_size = maxrows - thumb_top - thumb_bottom
        else:
            thumb_size = maxrows
            thumb_top = thumb_bottom = 0
        # create canvases to draw scrollbar
        scroll_top = SolidCanvas(self.trough_char, 1, thumb_top)
        scroll_thumb = SolidCanvas(self.thumb_char, 1, thumb_size)
        scroll_bottom = SolidCanvas(self.trough_char, 1, thumb_bottom)
        scroll_bar = CanvasCombine([
            (scroll_top, None, False),
            (scroll_thumb, None, False),
            (scroll_bottom, None, False),
        ])
        return CanvasJoin([
            (canv, None, True, maxcols - 1),
            (scroll_bar, None, False, 1),
        ])
