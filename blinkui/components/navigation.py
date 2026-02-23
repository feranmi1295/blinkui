from .base import Component


class TabBar(Component):
    """
    Bottom tab bar navigation.
    iOS style with icons and labels.

    Usage:
        TabBar(
            tabs=[
                Tab("Home",    icon="house",   screen=HomeScreen),
                Tab("Search",  icon="search",  screen=SearchScreen),
                Tab("Profile", icon="person",  screen=ProfileScreen),
            ]
        )
    """

    def __init__(self, tabs=None):
        super().__init__()
        self._tabs       = tabs or []
        self._selected   = 0
        self._tint       = "#007AFF"
        self._background = "#FFFFFF"
        self._border_top = True

    def selected(self, index):
        self._selected = index
        return self

    def tint(self, color):
        self._tint = color
        return self

    def to_dict(self):
        d = super().to_dict()
        d["tabs"]       = [t.to_dict() for t in self._tabs]
        d["selected"]   = self._selected
        d["tint"]       = self._tint
        d["border_top"] = self._border_top
        return d


class Tab:
    """Single tab item inside a TabBar."""

    def __init__(self, label="", icon="", screen=None):
        self._label  = label
        self._icon   = icon
        self._screen = screen.__name__ if screen else ""
        self._badge  = None

    def badge(self, value):
        self._badge = value
        return self

    def to_dict(self):
        return {
            "label":  self._label,
            "icon":   self._icon,
            "screen": self._screen,
            "badge":  self._badge,
        }


class NavigationBar(Component):
    """
    Top navigation bar with title and optional actions.

    Usage:
        NavigationBar(title="Home")
        NavigationBar(title="Home", large=False)
        NavigationBar(
            title="Home",
            left=IconButton("arrow.left").on_tap(self.go_back),
            right=IconButton("gear").on_tap(self.settings)
        )
    """

    def __init__(self, title="", left=None, right=None, large=True):
        super().__init__()
        self._title      = title
        self._left       = left
        self._right      = right
        self._background = "#F2F2F7"
        self._large      = large

    def large(self, value=True):
        self._large = value
        return self

    def to_dict(self):
        d = super().to_dict()
        d["title"] = self._title
        d["large"] = self._large
        d["left"]  = self._left.to_dict()  if self._left  else None
        d["right"] = self._right.to_dict() if self._right else None
        return d


class Toast(Component):
    """
    Brief notification that appears and disappears.

    Usage:
        Toast("Saved successfully", type="success")
        Toast("Something went wrong", type="error")
    """

    def __init__(self, message="", type="default"):
        super().__init__()
        self._message  = message
        self._type     = type
        self._duration = 3000

        color_map = {
            "success": "#34C759",
            "error":   "#FF3B30",
            "warning": "#FF9500",
            "default": "#1C1C1E",
        }
        self._background    = color_map.get(type, "#1C1C1E")
        self._color         = "#FFFFFF"
        self._corner_radius = 12

    def duration(self, ms):
        self._duration = ms
        return self

    def to_dict(self):
        d = super().to_dict()
        d["message"]  = self._message
        d["type"]     = self._type
        d["duration"] = self._duration
        return d