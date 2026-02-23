# ─────────────────────────────────────────
# Router — manages navigation between screens
# ─────────────────────────────────────────


class Router:
    """
    Manages the navigation stack.
    Handles push, pop, and data passing between screens.

    Usage:
        Router(
            routes={
                "home":      HomeScreen,
                "dashboard": DashboardScreen,
                "profile":   ProfileScreen,
            },
            entry="home"
        )
    """

    def __init__(self, routes: dict, entry: str):
        self._routes  = routes
        self._stack   = []      # navigation stack
        self._current = None    # current screen instance

        # validate entry route exists
        if entry not in routes:
            raise ValueError(
                f"[Router] Entry route '{entry}' not found in routes.\n"
                f"Available routes: {list(routes.keys())}"
            )

        # launch entry screen
        self._launch(entry)

    def _launch(self, route: str, data: dict = None):
        """Instantiate and mount a screen."""
        screen_class  = self._routes[route]
        screen        = screen_class()
        screen._navigator = self

        # pass data if provided
        if data:
            screen._route_data = data

        self._stack.append((route, screen))
        self._current = screen

        print(f"[Router] Navigated to: {route}")
        screen.on_mount()
        screen._render()

    def push(self, route: str, data: dict = None):
        """Navigate forward to a new screen."""
        if route not in self._routes:
            print(f"[Router] Route not found: {route}")
            print(f"[Router] Available: {list(self._routes.keys())}")
            return

        # unmount current screen
        if self._current:
            self._current.on_unmount()

        self._launch(route, data)

    def pop(self):
        """Go back to the previous screen."""
        if len(self._stack) <= 1:
            print("[Router] Already at root screen. Cannot go back.")
            return

        # unmount current
        _, current = self._stack.pop()
        current.on_unmount()

        # restore previous
        route, screen = self._stack[-1]
        self._current = screen
        screen._navigator = self

        print(f"[Router] Back to: {route}")
        screen._render()

    def replace(self, route: str, data: dict = None):
        """Replace current screen without adding to stack."""
        if self._current:
            self._current.on_unmount()
            self._stack.pop()

        self._launch(route, data)

    def reset(self, route: str):
        """Clear entire stack and start fresh."""
        # unmount all screens
        for _, screen in self._stack:
            screen.on_unmount()

        self._stack.clear()
        self._current = None

        print(f"[Router] Stack reset. Starting at: {route}")
        self._launch(route)

    @property
    def current_route(self):
        if self._stack:
            return self._stack[-1][0]
        return None

    @property
    def stack_depth(self):
        return len(self._stack)

    @property
    def can_go_back(self):
        return len(self._stack) > 1