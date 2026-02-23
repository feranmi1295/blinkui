from .base import Component


class TextField(Component):
    """
    Single line text input.

    Usage:
        TextField("Email").on_change(self.handle_email)
        TextField("Password").secure().on_change(self.handle_password)
    """

    def __init__(self, placeholder=""):
        super().__init__()
        self._placeholder  = placeholder
        self._value        = ""
        self._secure       = False      # password field
        self._keyboard     = "default"  # default, email, number, phone
        self._multiline    = False
        self._max_length   = None
        self._background   = "#FFFFFF"
        self._corner_radius = 10
        self._padding      = [12, 16, 12, 16]
        self._font_size    = 16

    def secure(self, value=True):
        self._secure = value
        return self

    def keyboard(self, type):
        # "default" "email" "number" "phone" "url"
        self._keyboard = type
        return self

    def multiline(self, value=True):
        self._multiline = value
        return self

    def max_length(self, value):
        self._max_length = value
        return self

    def value(self, text):
        self._value = text
        return self

    def to_dict(self):
        d = super().to_dict()
        d["placeholder"] = self._placeholder
        d["value"]       = self._value
        d["secure"]      = self._secure
        d["keyboard"]    = self._keyboard
        d["multiline"]   = self._multiline
        d["max_length"]  = self._max_length
        return d


class Toggle(Component):
    """
    iOS style on/off toggle switch.

    Usage:
        Toggle(value=True).on_change(self.handle_toggle)
    """

    def __init__(self, label="", value=False):
        super().__init__()
        self._label      = label
        self._value      = value
        self._tint       = "#34C759"    # iOS green

    def tint(self, color):
        self._tint = color
        return self

    def value(self, val):
        self._value = val
        return self

    def to_dict(self):
        d = super().to_dict()
        d["label"] = self._label
        d["value"] = self._value
        d["tint"]  = self._tint
        return d


class Slider(Component):
    """
    Horizontal slider for numeric values.

    Usage:
        Slider(min=0, max=100, value=50).on_change(self.handle_slide)
    """

    def __init__(self, min=0, max=100, value=0):
        super().__init__()
        self._min        = min
        self._max        = max
        self._value      = value
        self._step       = 1
        self._tint       = "#007AFF"

    def step(self, value):
        self._step = value
        return self

    def tint(self, color):
        self._tint = color
        return self

    def to_dict(self):
        d = super().to_dict()
        d["min"]   = self._min
        d["max"]   = self._max
        d["value"] = self._value
        d["step"]  = self._step
        d["tint"]  = self._tint
        return d


class Picker(Component):
    """
    Dropdown / wheel picker for selecting from options.

    Usage:
        Picker(options=["Red", "Green", "Blue"]).on_change(self.handle_pick)
    """

    def __init__(self, options=None, selected=0):
        super().__init__()
        self._options  = options or []
        self._selected = selected

    def selected(self, index):
        self._selected = index
        return self

    def to_dict(self):
        d = super().to_dict()
        d["options"]  = self._options
        d["selected"] = self._selected
        return d