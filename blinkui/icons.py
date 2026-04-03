"""
BlinkUI Icon Pack
Material-style icons as Unicode + named constants

Usage:
    from blinkui.icons import Icons

    Icon(Icons.HOME)
    Icon(Icons.SEARCH, size=24, color="#00FF88")
    Icon(Icons.HEART, size=20)
"""

class Icons:
    # ── Navigation ──
    HOME         = "home"
    BACK         = "back"
    FORWARD      = "forward"
    MENU         = "menu"
    CLOSE        = "close"
    SEARCH       = "search"
    SETTINGS     = "settings"
    MORE         = "more"

    # ── User ──
    USER         = "user"
    PROFILE      = "profile"
    USERS        = "users"
    LOGOUT       = "logout"
    LOGIN        = "login"

    # ── Actions ──
    ADD          = "add"
    EDIT         = "edit"
    DELETE       = "delete"
    SAVE         = "save"
    SHARE        = "share"
    COPY         = "copy"
    DOWNLOAD     = "download"
    UPLOAD       = "upload"
    REFRESH      = "refresh"
    FILTER       = "filter"
    SORT         = "sort"

    # ── Status ──
    CHECK        = "check"
    ERROR        = "error"
    WARNING      = "warning"
    INFO         = "info"
    SUCCESS      = "success"
    LOADING      = "loading"

    # ── Media ──
    CAMERA       = "camera"
    IMAGE        = "image"
    VIDEO        = "video"
    AUDIO        = "audio"
    PLAY         = "play"
    PAUSE        = "pause"
    STOP         = "stop"

    # ── Communication ──
    CHAT         = "chat"
    MAIL         = "mail"
    BELL         = "bell"
    PHONE        = "phone"
    SEND         = "send"

    # ── Finance ──
    WALLET       = "wallet"
    CARD         = "card"
    MONEY        = "money"
    CHART        = "chart"

    # ── Misc ──
    HEART        = "heart"
    STAR         = "star"
    BOOKMARK     = "bookmark"
    LOCATION     = "location"
    LOCK         = "lock"
    UNLOCK       = "unlock"
    EYE          = "eye"
    EYE_OFF      = "eye_off"
    CALENDAR     = "calendar"
    CLOCK        = "clock"
    LIGHTNING    = "lightning"
    MOON         = "moon"
    SUN          = "sun"
    GLOBE        = "globe"
    CODE         = "code"
    TERMINAL     = "terminal"
    AI           = "ai"
    ROBOT        = "robot"


# Unicode symbol map — used by ComponentFactory on Android
ICON_SYMBOLS = {
    # Navigation
    "home":      "⌂",
    "back":      "←",
    "forward":   "→",
    "menu":      "☰",
    "close":     "✕",
    "search":    "⌕",
    "settings":  "⚙",
    "more":      "⋯",

    # User
    "user":      "◉",
    "profile":   "◉",
    "users":     "◎",
    "logout":    "⇥",
    "login":     "⇤",

    # Actions
    "add":       "+",
    "edit":      "✎",
    "delete":    "🗑",
    "save":      "💾",
    "share":     "↗",
    "copy":      "⎘",
    "download":  "↓",
    "upload":    "↑",
    "refresh":   "↺",
    "filter":    "⊟",
    "sort":      "⇅",

    # Status
    "check":     "✓",
    "error":     "✕",
    "warning":   "⚠",
    "info":      "ℹ",
    "success":   "✓",
    "loading":   "◌",

    # Media
    "camera":    "⊙",
    "image":     "🖼",
    "video":     "▶",
    "audio":     "♪",
    "play":      "▶",
    "pause":     "⏸",
    "stop":      "⏹",

    # Communication
    "chat":      "◎",
    "mail":      "✉",
    "bell":      "🔔",
    "phone":     "☎",
    "send":      "➤",

    # Finance
    "wallet":    "◈",
    "card":      "▭",
    "money":     "₦",
    "chart":     "↗",

    # Misc
    "heart":     "♥",
    "star":      "★",
    "bookmark":  "🔖",
    "location":  "◎",
    "lock":      "🔒",
    "unlock":    "🔓",
    "eye":       "◉",
    "eye_off":   "◎",
    "calendar":  "📅",
    "clock":     "◷",
    "lightning": "⚡",
    "moon":      "☽",
    "sun":       "☀",
    "globe":     "🌐",
    "code":      "</>",
    "terminal":  "⌨",
    "ai":        "✦",
    "robot":     "⬡",
}

def get_symbol(name: str) -> str:
    return ICON_SYMBOLS.get(name.lower(), name)
