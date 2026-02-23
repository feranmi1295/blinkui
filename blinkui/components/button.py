from .base import Component


class Button(Component):
    """
    Tappable button.

    Usage:
        Button("Get Started").on_tap(self.handle_tap)
        Button("Delete").color("#FF3B30").on_tap(self.delete)
    """
    def __init__(self, label=""):
        super().__init__()
        self._label      = str(label)
        self._background = "#007AFF"   # iOS blue
        self._color      = "#FFFFFF"
        self._font_size  = 16
        self._bold       = True
        self._corner_radius = 12
        self._padding    = [14, 20, 14, 20]

    def to_dict(self):
        d = super().to_dict()
        d["label"] = self._label
        return d


class IconButton(Component):
    """
    Button with just an icon.

    Usage:
        IconButton("heart").on_tap(self.like)
    """
    def __init__(self, icon=""):
        super().__init__()
        self._icon       = icon
        self._background = "transparent"
        self._color      = "#007AFF"

    def to_dict(self):
        d = super().to_dict()
        d["icon"] = self._icon
        return d