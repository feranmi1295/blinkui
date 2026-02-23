# ─────────────────────────────────────────
# Theme system
# One object controls the entire app's
# visual identity
# ─────────────────────────────────────────


# iOS inspired default colors
_DEFAULT_LIGHT = {
    "primary":          "#007AFF",   # iOS blue
    "primary_dark":     "#0055B3",
    "secondary":        "#5856D6",   # iOS purple
    "success":          "#34C759",   # iOS green
    "warning":          "#FF9500",   # iOS orange
    "danger":           "#FF3B30",   # iOS red
    "background":       "#F2F2F7",   # iOS light background
    "surface":          "#FFFFFF",   # card / sheet background
    "text":             "#1C1C1E",   # primary text
    "text_secondary":   "#8E8E93",   # secondary text
    "text_tertiary":    "#AEAEB2",   # placeholder text
    "border":           "#E5E5EA",   # dividers and borders
    "overlay":          "rgba(0,0,0,0.4)",
}

_DEFAULT_DARK = {
    "primary":          "#0A84FF",
    "primary_dark":     "#0055B3",
    "secondary":        "#5E5CE6",
    "success":          "#30D158",
    "warning":          "#FF9F0A",
    "danger":           "#FF453A",
    "background":       "#000000",
    "surface":          "#1C1C1E",
    "text":             "#FFFFFF",
    "text_secondary":   "#8E8E93",
    "text_tertiary":    "#636366",
    "border":           "#38383A",
    "overlay":          "rgba(0,0,0,0.6)",
}


class Palette:
    """A set of colors for one color mode."""

    def __init__(self, colors: dict):
        self._colors = colors

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return self._colors.get(name, "#000000")

    def get(self, key, fallback="#000000"):
        return self._colors.get(key, fallback)


class Theme:
    """
    Controls the entire visual identity of a BlinkUI app.

    Usage — default iOS theme:
        App(entry=HomeScreen).run()

    Usage — custom theme:
        theme = Theme(
            primary="#6C63FF",
            font="Poppins",
            radius=16
        )
        App(entry=HomeScreen, theme=theme).run()

    Usage — full dark/light control:
        theme = Theme(
            light={"primary": "#007AFF", "background": "#FFFFFF"},
            dark={"primary":  "#0A84FF", "background": "#000000"}
        )
    """

    def __init__(
        self,
        primary=None,
        secondary=None,
        success=None,
        warning=None,
        danger=None,
        background=None,
        surface=None,
        text=None,
        font="SF Pro Display",
        font_mono="SF Mono",
        radius=12,
        light: dict = None,
        dark:  dict  = None,
    ):
        # build light palette
        light_colors = dict(_DEFAULT_LIGHT)
        if light:
            light_colors.update(light)

        # apply individual overrides to both modes
        overrides = {
            k: v for k, v in {
                "primary":    primary,
                "secondary":  secondary,
                "success":    success,
                "warning":    warning,
                "danger":     danger,
                "background": background,
                "surface":    surface,
                "text":       text,
            }.items() if v is not None
        }
        light_colors.update(overrides)

        # build dark palette
        dark_colors = dict(_DEFAULT_DARK)
        if dark:
            dark_colors.update(dark)
        dark_colors.update(overrides)

        self.light     = Palette(light_colors)
        self.dark      = Palette(dark_colors)
        self.font      = font
        self.font_mono = font_mono
        self.radius    = radius

        # active palette — switches based on system preference
        # on device this reads the OS setting
        # for now default to light
        self._mode     = "light"
        self.colors    = self.light

    def set_mode(self, mode: str):
        """Switch between light and dark mode."""
        if mode not in ("light", "dark"):
            return
        self._mode  = mode
        self.colors = self.light if mode == "light" else self.dark
        print(f"[Theme] Switched to {mode} mode")

    def toggle_mode(self):
        """Toggle between light and dark."""
        self.set_mode("dark" if self._mode == "light" else "light")

    def to_dict(self):
        return {
            "mode":      self._mode,
            "font":      self.font,
            "radius":    self.radius,
            "primary":   self.colors.primary,
            "background": self.colors.background,
            "surface":   self.colors.surface,
            "text":      self.colors.text,
        }

    def __repr__(self):
        return f"<Theme mode={self._mode} primary={self.colors.primary}>"


# global default theme — used when developer doesn't specify one
_default_theme = Theme()


def get_theme() -> Theme:
    return _default_theme


def set_theme(theme: Theme):
    global _default_theme
    _default_theme = theme