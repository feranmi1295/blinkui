"""
BlinkUI Global Store
Shared reactive state across all screens.
"""

from typing import Any, Callable, List


class Store:
    def __init__(self, initial_value: Any):
        self._value      = initial_value
        self._listeners: List[Callable] = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self._notify()

    def subscribe(self, listener: Callable):
        self._listeners.append(listener)

    def unsubscribe(self, listener: Callable):
        self._listeners = [l for l in self._listeners if l != listener]

    def _notify(self):
        for listener in self._listeners:
            try:
                listener(self._value)
            except Exception as e:
                print(f"[Store] Listener error: {e}")

    def __repr__(self):
        return f"Store({self._value!r})"


def store(initial_value: Any) -> Store:
    """Create a global reactive store."""
    return Store(initial_value)
