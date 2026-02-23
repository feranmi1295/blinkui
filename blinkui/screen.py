from .state import StateDescriptor


class Screen:
    """
    Base class for all BlinkUI screens.
    Developers inherit from this and implement build().

    Usage:
        class HomeScreen(Screen):
            count = state(0)

            def build(self):
                return VStack(
                    Text(f"{self.count}"),
                    Button("Tap").on_tap(self.increment)
                )

            def increment(self):
                self.count += 1
    """

    def __init__(self):
        self._navigator  = None
        self._mounted    = False
        self._tree       = None

    def build(self):
        """
        Override this to describe your UI.
        Called every time state changes.
        Must return a Component.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement build()"
        )

    def _on_state_change(self, key, value):
        """Called automatically when any state() variable changes."""
        print(f"[Screen] State changed: {key} = {value}")
        self._render()

    def _render(self):
        """Re-runs build() and gets the new component tree."""
        new_tree = self.build()
        self._tree = new_tree
        print(f"[Screen] Rendered: {self.__class__.__name__}")

        # on mobile this sends tree to C runtime for reconciling
        # for now print the tree dict
        import json
        print(json.dumps(self._tree.to_dict(), indent=2))

    def on_mount(self):
        """Called when screen first appears. Override to run setup."""
        pass

    def on_unmount(self):
        """Called when screen is removed. Override to cleanup."""
        pass

    def navigate(self, route, data=None):
        """Navigate to another screen by route name."""
        if self._navigator:
            self._navigator.push(route, data)
        else:
            print(f"[Screen] Navigate to: {route}")