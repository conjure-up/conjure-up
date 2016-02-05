# Copyright 2015 Canonical, Ltd.
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

""" Palette Loader """

# Palette
orange        = "#f60"
light_orange  = "#f80"
dark_magenta  = "#608"
light_magenta = "#f0f"
light_red     = "#f00"
light_green   = "#0d0"
white         = "white"
black         = "black"
light_gray    = "g82"
cool_gray     = "g50"
warm_gray     = "g15"
blue          = "#08f"
dark_blue     = "#00f"

# Styles
STYLES = [
    ("frame_header", "", "", "", white, orange),
    ("frame_subheader", "", "", "", white, warm_gray),
    ("frame_excerpt", "", "", "", cool_gray, ""),
    ("frame_footer", "", "", "", white, warm_gray),
    ("body", "", "", "", white, ""),
    ("button_primary", "", "", "", white, cool_gray),
    ("button_primary focus", "", "", "", white, light_orange),
    ("button_secondary", "", "", "", white, cool_gray),
    ("button_secondary focus", "", "", "", white, light_orange),
    ("info_minor", "", "", "", warm_gray, ""),
    ("info_major", "", "", "", light_green, ""),
    ("error_major", "", "", "", light_red, ""),
    ("status_info", "", "", "", light_green, warm_gray),
    ("status_error", "", "", "", light_red, warm_gray),
    ("string_input", "", "", "", white, cool_gray),
    ("string_input focus", "", "", "", white, orange),
    ("dialog", "", "", "", white, warm_gray),
    ("radio_input", "", "", "", white, warm_gray),
    ("radio_input focus", "", "", "", orange, warm_gray),
    ("header_title", "", "", "", orange, ""),
    ("pending_icon_on", "", "", "", blue, ""),
    ("pending_icon", "", "", "", blue, ""),
    ("error_icon", "", "", "", light_red, ""),
    ("success_icon", "", "", "", light_green, ""),
    ("column_header", "", "", "", white, blue),
    ('deploy_highlight_start', "", "", "", warm_gray, light_green),
    ('deploy_highlight_end', "", "", "", warm_gray, cool_gray),
    ('disabled_button', "", "", "", light_gray, warm_gray),
    ('disabled_button_focus', "", "", "", light_gray, warm_gray),
    ('divider_line', "", "", "", warm_gray, ""),
    ('filter', "", "", "", black, light_gray),
    ('filter_focus', "", "", "", white, warm_gray),
    ('focus', "", "", "", white, warm_gray),
    ('radio focus', "", "", "", white, dark_magenta),
    ('status_extra', "", "", "", light_gray, warm_gray),
    ('error', "", "", "", white, light_red),
    ('info', "", "", "", light_green, ''),
    ('label', "", "", "", light_gray, ''),
]
