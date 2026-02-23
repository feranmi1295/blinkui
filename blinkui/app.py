from .screen import Screen


class App:
    """
    Entry point for every BlinkUI app.

    Usage:
        from blinkui import App
        from screens.home import HomeScreen

        App(entry=HomeScreen).run()
    """

    def __init__(self, entry, theme=None):
        self._entry  = entry
        self._theme  = theme
        self._screen = None

    def run(self):
        print("[App] BlinkUI starting...")

        # instantiate the entry screen
        self._screen = self._entry()

        # mount and render
        self._screen.on_mount()
        self._screen._render()

        print("[App] App running")