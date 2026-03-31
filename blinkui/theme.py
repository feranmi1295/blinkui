"""
BlinkUI Theme System

BlinkUI's design language:
- Dark by default
- Electric green accent
- Sharp, technical, precise
- No unnecessary decoration
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BlinkTheme:
    # ── Core colors ──
    background:   str = "#0F0F0F"   # near black
    surface:      str = "#1A1A1A"   # card / elevated surfaces
    surface_high: str = "#242424"   # inputs, selected states
    border:       str = "#2A2A2A"   # subtle borders

    # ── Accent ──
    accent:       str = "#00FF88"   # electric green — BlinkUI signature
    accent_dim:   str = "#00CC6A"   # pressed state
    accent_muted: str = "#003D20"   # backgrounds behind accent

    # ── Text ──
    text:         str = "#FFFFFF"   # primary text
    text_secondary: str = "#999999" # secondary / labels
    text_muted:   str = "#555555"   # placeholder / disabled
    text_on_accent: str = "#0F0F0F" # text on top of accent color

    # ── Semantic colors ──
    danger:       str = "#FF3B30"
    warning:      str = "#FF9500"
    success:      str = "#00FF88"   # same as accent
    info:         str = "#0A84FF"

    # ── Spacing ──
    spacing_xs:   int = 4
    spacing_sm:   int = 8
    spacing_md:   int = 16
    spacing_lg:   int = 24
    spacing_xl:   int = 32

    # ── Typography ──
    font_xs:      int = 11
    font_sm:      int = 13
    font_md:      int = 16
    font_lg:      int = 20
    font_xl:      int = 28
    font_xxl:     int = 36

    # ── Shape ──
    radius_sm:    int = 6
    radius_md:    int = 12
    radius_lg:    int = 20
    radius_full:  int = 999  # pill shape


# ── Global theme instance ──
_current_theme = BlinkTheme()

def get_theme() -> BlinkTheme:
    return _current_theme

def set_theme(theme: BlinkTheme):
    global _current_theme
    _current_theme = theme

# ── Preset themes ──

def dark_theme() -> BlinkTheme:
    """BlinkUI default — dark, electric green"""
    return BlinkTheme()

def light_theme() -> BlinkTheme:
    """Light variant"""
    return BlinkTheme(
        background    = "#F5F5F5",
        surface       = "#FFFFFF",
        surface_high  = "#EFEFEF",
        border        = "#E0E0E0",
        text          = "#0F0F0F",
        text_secondary= "#666666",
        text_muted    = "#AAAAAA",
        text_on_accent= "#FFFFFF",
    )

def ocean_theme() -> BlinkTheme:
    """Deep blue variant"""
    return BlinkTheme(
        background    = "#050D18",
        surface       = "#0A1628",
        surface_high  = "#112240",
        border        = "#1E3A5F",
        accent        = "#00D4FF",
        accent_dim    = "#00AACC",
        accent_muted  = "#001F2E",
        text_on_accent= "#050D18",
    )

def ember_theme() -> BlinkTheme:
    """Warm dark variant"""
    return BlinkTheme(
        background    = "#0F0A08",
        surface       = "#1A1208",
        surface_high  = "#241A0A",
        border        = "#3D2A10",
        accent        = "#FF6B00",
        accent_dim    = "#CC5500",
        accent_muted  = "#2E1800",
        text_on_accent= "#0F0A08",
    )
