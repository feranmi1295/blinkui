from .base import Component


class Image(Component):
    """
    Displays an image from a path or URL.

    Usage:
        Image("avatar.png").size(80).round()
        Image("https://example.com/photo.jpg").width(200).height(150)
    """

    def __init__(self, source=""):
        super().__init__()
        self._source    = source
        self._fit       = "cover"   # cover, contain, fill
        self._alt       = ""

    def fit(self, mode):
        # "cover" "contain" "fill"
        self._fit = mode
        return self

    def alt(self, text):
        self._alt = text
        return self

    def to_dict(self):
        d = super().to_dict()
        d["source"] = self._source
        d["fit"]    = self._fit
        d["alt"]    = self._alt
        return d


class Avatar(Component):
    """
    Circular avatar image. Falls back to initials if no image.

    Usage:
        Avatar("photo.png").size(48)
        Avatar(initials="JD").size(48).color("#007AFF")
    """

    def __init__(self, source="", initials=""):
        super().__init__()
        self._source   = source
        self._initials = initials
        self._size_val = 40
        self._background = "#007AFF"
        self._color      = "#FFFFFF"

    def size(self, value):
        self._size_val       = value
        self._width          = value
        self._height         = value
        self._corner_radius  = value / 2
        return self

    def to_dict(self):
        d = super().to_dict()
        d["source"]   = self._source
        d["initials"] = self._initials
        d["size"]     = self._size_val
        return d