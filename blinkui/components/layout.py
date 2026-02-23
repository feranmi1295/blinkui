from .base import Component


class VStack(Component):
    """
    Vertical stack — arranges children top to bottom.

    Usage:
        VStack(
            Text("Hello"),
            Button("Tap me")
        ).spacing(16).padding(20)
    """
    def __init__(self, *children):
        super().__init__(*children)
        self._spacing = 8


class HStack(Component):
    """
    Horizontal stack — arranges children left to right.

    Usage:
        HStack(
            Image("avatar.png"),
            Text("John Doe")
        ).spacing(12)
    """
    def __init__(self, *children):
        super().__init__(*children)
        self._spacing = 8


class ZStack(Component):
    """
    Z stack — layers children on top of each other.

    Usage:
        ZStack(
            Image("background.png"),
            Text("Overlay text")
        )
    """
    pass


class ScrollView(Component):
    """
    Scrollable container.

    Usage:
        ScrollView(
            VStack(...)
        )
    """
    def __init__(self, *children):
        super().__init__(*children)
        self._scroll_direction = "vertical"

    def horizontal(self):
        self._scroll_direction = "horizontal"
        return self


class Spacer(Component):
    """
    Flexible space that fills available room.

    Usage:
        HStack(
            Text("Left"),
            Spacer(),
            Text("Right")
        )
    """
    def __init__(self):
        super().__init__()


class Divider(Component):
    """
    Horizontal line divider.

    Usage:
        VStack(
            Text("Above"),
            Divider(),
            Text("Below")
        )
    """
    def __init__(self):
        super().__init__()
        self._color = "#E5E5EA"