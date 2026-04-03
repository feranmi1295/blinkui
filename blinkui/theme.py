"""
BlinkUI Theme System

Fully customizable — any colors, any style.
Dark theme is just the default.

Usage:
    from blinkui.theme import Theme, set_theme, dark, light, ocean, ember

    # use built-in theme
    set_theme(ocean())

    # or fully custom
    set_theme(Theme(
        background   = "#FFFFFF",
        surface      = "#F5F5F5",
        accent       = "#6C63FF",
        text         = "#1A1A1A",
        text_secondary = "#666666",
    ))

    # in your screen
    from blinkui.theme import get_theme
    t = get_theme()
    Button("Tap").background(t.accent).color(t.text_on_accent)
"""

from dataclasses import dataclass, field

@dataclass
class Theme:
    # ── Backgrounds ──
    background:     str = "#0F0F0F"   # main screen bg
    surface:        str = "#1A1A1A"   # card / elevated
    surface_high:   str = "#242424"   # inputs, hover
    border:         str = "#2A2A2A"   # subtle borders

    # ── Accent ──
    accent:         str = "#00FF88"   # primary action color
    accent_dark:    str = "#00CC6A"   # pressed state
    accent_muted:   str = "#003D20"   # accent backgrounds

    # ── Text ──
    text:           str = "#FFFFFF"
    text_secondary: str = "#999999"
    text_muted:     str = "#555555"
    text_on_accent: str = "#0F0F0F"   # text on top of accent

    # ── Semantic ──
    danger:         str = "#FF3B30"
    warning:        str = "#FF9500"
    success:        str = "#00FF88"
    info:           str = "#0A84FF"

    # ── Spacing ──
    space_xs:  int = 4
    space_sm:  int = 8
    space_md:  int = 16
    space_lg:  int = 24
    space_xl:  int = 32

    # ── Typography ──
    font_xs:  int = 11
    font_sm:  int = 13
    font_md:  int = 16
    font_lg:  int = 20
    font_xl:  int = 28
    font_xxl: int = 36

    # ── Shape ──
    radius_sm:   int = 6
    radius_md:   int = 12
    radius_lg:   int = 20
    radius_full: int = 999


# ── Global theme instance ──
_theme = Theme()

def get_theme() -> Theme:
    return _theme

def set_theme(theme: Theme):
    global _theme
    _theme = theme


# ── Built-in themes ──

def dark() -> Theme:
    """BlinkUI default — dark + electric green"""
    return Theme()

def light() -> Theme:
    """Clean light theme"""
    return Theme(
        background     = "#F8F9FA",
        surface        = "#FFFFFF",
        surface_high   = "#F0F0F0",
        border         = "#E0E0E0",
        accent         = "#007AFF",
        accent_dark    = "#0056CC",
        accent_muted   = "#E8F0FF",
        text           = "#1A1A1A",
        text_secondary = "#666666",
        text_muted     = "#AAAAAA",
        text_on_accent = "#FFFFFF",
        success        = "#34C759",
        danger         = "#FF3B30",
        warning        = "#FF9500",
        info           = "#007AFF",
    )

def ocean() -> Theme:
    """Deep ocean blue"""
    return Theme(
        background     = "#050D18",
        surface        = "#0A1628",
        surface_high   = "#112240",
        border         = "#1E3A5F",
        accent         = "#00D4FF",
        accent_dark    = "#00AACC",
        accent_muted   = "#001F2E",
        text           = "#E8F4FD",
        text_secondary = "#7BA7C4",
        text_muted     = "#3A6080",
        text_on_accent = "#050D18",
        success        = "#00D4FF",
    )

def ember() -> Theme:
    """Warm ember orange"""
    return Theme(
        background     = "#0F0A08",
        surface        = "#1A1208",
        surface_high   = "#241A0A",
        border         = "#3D2A10",
        accent         = "#FF6B00",
        accent_dark    = "#CC5500",
        accent_muted   = "#2E1800",
        text           = "#FFF5ED",
        text_secondary = "#C4906A",
        text_muted     = "#6B4A2A",
        text_on_accent = "#0F0A08",
        success        = "#FF6B00",
        danger         = "#FF3B30",
    )

def midnight() -> Theme:
    """Deep purple midnight"""
    return Theme(
        background     = "#08070F",
        surface        = "#12101E",
        surface_high   = "#1E1A30",
        border         = "#2D2845",
        accent         = "#8B5CF6",
        accent_dark    = "#6D28D9",
        accent_muted   = "#1A0F35",
        text           = "#F0EEFF",
        text_secondary = "#9B8EC4",
        text_muted     = "#4A3F6B",
        text_on_accent = "#FFFFFF",
        success        = "#34D399",
        danger         = "#F87171",
        info           = "#60A5FA",
    )

def rose() -> Theme:
    """Rose pink"""
    return Theme(
        background     = "#0F080A",
        surface        = "#1A0E12",
        surface_high   = "#24141A",
        border         = "#3D1F28",
        accent         = "#FF2D78",
        accent_dark    = "#CC1A5A",
        accent_muted   = "#2E0515",
        text           = "#FFF0F5",
        text_secondary = "#C47088",
        text_muted     = "#6B3045",
        text_on_accent = "#FFFFFF",
        success        = "#34C759",
        danger         = "#FF3B30",
    )

def forest() -> Theme:
    """Deep forest green"""
    return Theme(
        background     = "#070F08",
        surface        = "#0D1A0E",
        surface_high   = "#142416",
        border         = "#1F3D22",
        accent         = "#22C55E",
        accent_dark    = "#16A34A",
        accent_muted   = "#052010",
        text           = "#F0FFF4",
        text_secondary = "#74B987",
        text_muted     = "#3A6B45",
        text_on_accent = "#070F08",
        success        = "#22C55E",
        danger         = "#FF3B30",
        info           = "#0EA5E9",
    )

def nord() -> Theme:
    """Nord inspired — cool greys"""
    return Theme(
        background     = "#2E3440",
        surface        = "#3B4252",
        surface_high   = "#434C5E",
        border         = "#4C566A",
        accent         = "#88C0D0",
        accent_dark    = "#81A1C1",
        accent_muted   = "#2E3440",
        text           = "#ECEFF4",
        text_secondary = "#D8DEE9",
        text_muted     = "#4C566A",
        text_on_accent = "#2E3440",
        success        = "#A3BE8C",
        danger         = "#BF616A",
        warning        = "#EBCB8B",
        info           = "#88C0D0",
    )

def solarized() -> Theme:
    """Solarized dark"""
    return Theme(
        background     = "#002B36",
        surface        = "#073642",
        surface_high   = "#0D4A5A",
        border         = "#586E75",
        accent         = "#268BD2",
        accent_dark    = "#1A6AA8",
        accent_muted   = "#001F28",
        text           = "#FDF6E3",
        text_secondary = "#93A1A1",
        text_muted     = "#586E75",
        text_on_accent = "#FDF6E3",
        success        = "#859900",
        danger         = "#DC322F",
        warning        = "#B58900",
        info           = "#268BD2",
    )


# convenience aliases
get = get_theme
