from .base import Component


class Text(Component):
    """
    Displays text.

    Usage:
        Text("Hello World").size(24).bold().color("#1C1C1E")
    """
    def __init__(self, content=""):
        super().__init__()
        self._content = str(content)
        self._color   = "#1C1C1E"

    def to_dict(self):
        d = super().to_dict()
        d["content"] = self._content
        return d


class Heading(Text):
    """
    Large heading text. Size 28 bold by default.

    Usage:
        Heading("Welcome Back")
    """
    def __init__(self, content=""):
        super().__init__(content)
        self._font_size = 28
        self._bold      = True


class Label(Text):
    """
    Small label text. Size 12 subtle color by default.

    Usage:
        Label("Last updated 2 mins ago")
    """
    def __init__(self, content=""):
        super().__init__(content)
        self._font_size = 12
        self._color     = "#8E8E93"


class Badge(Component):
    """
    Small pill shaped badge.

    Usage:
        Badge("New").color("#FF3B30")
    """
    def __init__(self, content=""):
        super().__init__()
        self._content    = str(content)
        self._background = "#FF3B30"
        self._color      = "#FFFFFF"
        self._font_size  = 11
        self._bold       = True

    def to_dict(self):
        d = super().to_dict()
        d["content"] = self._content
        return d