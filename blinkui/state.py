# ─────────────────────────────────────────
# State descriptor
# Works like a normal variable but notifies
# the runtime when its value changes
# ─────────────────────────────────────────

class StateDescriptor:
    """
    Descriptor that tracks state changes.
    When value changes, tells the screen
    to re-render automatically.
    """

    def __init__(self, default):
        self.default = default
        self.name    = None

    def __set_name__(self, owner, name):
        self.name = f"_state_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, self.default)

    def __set__(self, obj, value):
        old_value = getattr(obj, self.name, self.default)
        setattr(obj, self.name, value)

        # only re-render if value actually changed
        if old_value != value and hasattr(obj, "_on_state_change"):
            obj._on_state_change(self.name, value)


def state(default):
    """
    Declare a reactive state variable.

    Usage:
        class HomeScreen(Screen):
            count = state(0)
            name  = state("John")
    """
    return StateDescriptor(default)