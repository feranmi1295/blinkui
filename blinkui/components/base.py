# ─────────────────────────────────────────
# Base component
# Every BlinkUI component inherits from this
# ─────────────────────────────────────────

class Component:
    """
    Base class for all BlinkUI components.
    Supports method chaining for styling.
    """

    def __init__(self, *children):
        self._children        = list(children)
        self._font_size       = 16
        self._bold            = False
        self._italic          = False
        self._color           = None
        self._background      = None
        self._width           = None
        self._height          = None
        self._padding         = [0, 0, 0, 0]  # top right bottom left
        self._margin          = [0, 0, 0, 0]
        self._corner_radius   = 0
        self._opacity         = 1.0
        self._visible         = True
        self._on_tap          = None
        self._on_change       = None
        self._spacing         = 8
        self._align           = "start"
        self._animation       = None

    # ── Styling methods — all return self for chaining ──

    def size(self, font_size):
        self._font_size = font_size
        return self

    def bold(self, value=True):
        self._bold = value
        return self

    def italic(self, value=True):
        self._italic = value
        return self

    def color(self, color):
        self._color = color
        return self

    def background(self, color):
        self._background = color
        return self

    def width(self, value):
        self._width = value
        return self

    def height(self, value):
        self._height = value
        return self

    def padding(self, top=0, right=None, bottom=None, left=None):
        # support padding(16) for all sides
        if right is None:
            right = bottom = left = top
        elif bottom is None:
            bottom = top
            left   = right
        self._padding = [top, right, bottom, left]
        return self

    def margin(self, top=0, right=None, bottom=None, left=None):
        if right is None:
            right = bottom = left = top
        elif bottom is None:
            bottom = top
            left   = right
        self._margin = [top, right, bottom, left]
        return self

    def corner_radius(self, value):
        self._corner_radius = value
        return self

    def round(self, value=999):
        self._corner_radius = value
        return self

    def opacity(self, value):
        self._opacity = value
        return self

    def visible(self, value=True):
        self._visible = value
        return self

    def spacing(self, value):
        self._spacing = value
        return self

    def align(self, value):
        # "start" "center" "end"
        self._align = value
        return self

    def center(self):
        self._align = "center"
        return self

    # ── Event methods ──

    def on_tap(self, callback):
        self._on_tap = callback
        return self

    def on_change(self, callback):
        self._on_change = callback
        return self

    # ── Animation ──

    def animate(self, duration=300, curve="easeOut", **props):
        self._animation = {
            "duration": duration,
            "curve":    curve,
            "props":    props
        }
        return self

    # ── Serialization ──
    # Converts component tree to dict
    # C runtime reads this dict to build native views

    def to_dict(self):
        return {
            "type":          self.__class__.__name__,
            "font_size":     self._font_size,
            "bold":          self._bold,
            "italic":        self._italic,
            "color":         self._color,
            "background":    self._background,
            "width":         self._width,
            "height":        self._height,
            "padding":       self._padding,
            "margin":        self._margin,
            "corner_radius": self._corner_radius,
            "opacity":       self._opacity,
            "visible":       self._visible,
            "spacing":       self._spacing,
            "align":         self._align,
            "animation":     self._animation,
            "children": [
                c.to_dict() if isinstance(c, Component) else str(c)
                for c in self._children
            ]
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} children={len(self._children)}>"