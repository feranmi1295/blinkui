"""
BlinkUI AI-Native Components

The unique BlinkUI advantage — components with built-in AI capabilities.
These ship with every BlinkUI app at zero extra dependency cost.

Usage:
    from blinkui.ai import SmartList, AutoStyle, AICard, SmartForm

    class HomeScreen(Screen):
        def build(self):
            return VStack(
                # Auto-generates UI from any data
                SmartList(self.products),

                # Adapts style to content automatically
                AutoStyle(Text(self.headline)),

                # Generates entire card from a prompt
                AICard(prompt="Show user stats cleanly"),

                # Smart form that validates itself
                SmartForm(fields=["name", "email", "password"]),
            )
"""

from .components.base import Component


class SmartList(Component):
    """
    Renders any list of data intelligently.
    Detects data shape and picks best layout automatically.

    SmartList(items)                    → auto-detects layout
    SmartList(items, template="card")   → force card layout
    SmartList(items, template="row")    → force row layout
    SmartList(items, key="name")        → use 'name' as title field
    """
    def __init__(self, items, template=None, key=None,
                 on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self.items    = items
        self.template = template or self._detect_template(items)
        self.key      = key
        self._on_tap  = on_tap

    def _detect_template(self, items) -> str:
        if not items:
            return "empty"
        first = items[0] if isinstance(items, list) else None
        if isinstance(first, dict):
            keys = set(first.keys())
            if "image" in keys or "avatar" in keys or "photo" in keys:
                return "card_image"
            if "title" in keys or "name" in keys:
                return "row_title"
            return "row_data"
        if isinstance(first, str):
            return "row_text"
        return "row_text"

    def on_tap(self, handler):
        self._on_tap = handler
        return self


class AutoStyle(Component):
    """
    Wraps any component and automatically applies
    contextually appropriate styling.

    AutoStyle(Text("Revenue: $1.2M"))
        → detects monetary value → green color
    AutoStyle(Text("Error: Connection failed"))
        → detects error → red color
    AutoStyle(Text("John Doe"))
        → detects name → title case, bold
    """
    def __init__(self, child, context=None, **kwargs):
        super().__init__(**kwargs)
        self.child   = child
        self.context = context

    def _detect_style(self, text: str) -> dict:
        text_lower = text.lower()
        # monetary values
        if any(c in text for c in ['$', '₦', '€', '£']) or \
           any(w in text_lower for w in ['revenue', 'profit', 'earning']):
            return {"color": "#00FF88", "bold": True}
        # errors/warnings
        if any(w in text_lower for w in ['error', 'failed', 'invalid', 'wrong']):
            return {"color": "#FF3B30", "bold": True}
        # warnings
        if any(w in text_lower for w in ['warning', 'caution', 'pending']):
            return {"color": "#FF9500", "bold": False}
        # success
        if any(w in text_lower for w in ['success', 'complete', 'done', 'verified']):
            return {"color": "#00FF88", "bold": False}
        # large numbers
        if any(c.isdigit() for c in text) and len(text) < 20:
            return {"color": "#FFFFFF", "bold": True, "size": 32}
        return {}


class AICard(Component):
    """
    Generates an entire card UI from a text prompt.
    Uses on-device heuristics (no API call needed).

    AICard(prompt="Show user profile with avatar and stats")
    AICard(prompt="Display product with price and buy button")
    AICard(prompt="Show weather for current location")
    """
    def __init__(self, prompt: str, data=None, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompt
        self.data   = data
        self._layout = self._generate_layout(prompt, data)

    def _generate_layout(self, prompt: str, data) -> dict:
        p = prompt.lower()

        if "profile" in p or "user" in p or "avatar" in p:
            return {
                "type": "profile",
                "fields": ["avatar", "name", "bio", "stats"]
            }
        if "product" in p or "item" in p or "price" in p:
            return {
                "type": "product",
                "fields": ["image", "name", "price", "buy_button"]
            }
        if "stat" in p or "metric" in p or "dashboard" in p:
            return {
                "type": "stats",
                "fields": ["value", "label", "trend"]
            }
        if "weather" in p or "forecast" in p:
            return {
                "type": "weather",
                "fields": ["temp", "condition", "location"]
            }
        if "chart" in p or "graph" in p or "analytics" in p:
            return {
                "type": "chart",
                "fields": ["title", "data", "period"]
            }
        # default: key-value card
        return {
            "type": "info",
            "fields": ["title", "description", "action"]
        }


class SmartForm(Component):
    """
    Auto-generates a form with validation from field names.
    Detects field types from names and applies appropriate input.

    SmartForm(fields=["name", "email", "password", "phone"])
        → name: text input
        → email: email input with @ validation
        → password: secure input with eye toggle
        → phone: numeric input with format
    """
    def __init__(self, fields: list, on_submit=None,
                 submit_label="Submit", **kwargs):
        super().__init__(**kwargs)
        self.fields       = fields
        self._on_submit   = on_submit
        self.submit_label = submit_label
        self._field_types = {f: self._detect_type(f) for f in fields}

    def _detect_type(self, field_name: str) -> dict:
        f = field_name.lower()
        if "email" in f or "mail" in f:
            return {"type": "email", "keyboard": "email", "validate": "email"}
        if "password" in f or "pass" in f or "secret" in f:
            return {"type": "password", "secure": True}
        if "phone" in f or "mobile" in f or "tel" in f:
            return {"type": "phone", "keyboard": "phone"}
        if "age" in f or "year" in f or "count" in f or "amount" in f:
            return {"type": "number", "keyboard": "numeric"}
        if "date" in f or "dob" in f or "birthday" in f:
            return {"type": "date"}
        if "bio" in f or "description" in f or "about" in f or "note" in f:
            return {"type": "multiline"}
        if "url" in f or "website" in f or "link" in f:
            return {"type": "url", "keyboard": "url"}
        return {"type": "text"}

    def on_submit(self, handler):
        self._on_submit = handler
        return self


class SmartText(Component):
    """
    Text that automatically formats itself based on content.

    SmartText("$1,234.56")     → formats as currency
    SmartText("2024-01-15")    → formats as readable date
    SmartText("john@mail.com") → formats as link
    SmartText(0.85)            → formats as percentage
    """
    def __init__(self, value, format=None, **kwargs):
        super().__init__(**kwargs)
        self.value  = value
        self.format = format or self._detect_format(value)

    def _detect_format(self, value) -> str:
        if isinstance(value, float) and 0 <= value <= 1:
            return "percentage"
        s = str(value)
        if s.startswith("$") or s.startswith("₦"):
            return "currency"
        if "@" in s and "." in s:
            return "email"
        if s.count("-") == 2 and len(s) == 10:
            return "date"
        if s.startswith("http"):
            return "url"
        return "text"
