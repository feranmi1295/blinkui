from .base import Component


class Card(Component):
    """
    Elevated surface for grouping content.
    iOS style with subtle shadow and rounded corners.

    Usage:
        Card(
            VStack(
                Text("Title").bold(),
                Text("Subtitle").color("#8E8E93")
            )
        ).padding(16)

        Card(
            Text("Simple card")
        ).on_tap(self.handle_tap)
    """

    def __init__(self, *children):
        super().__init__(*children)
        self._background    = "#FFFFFF"
        self._corner_radius = 12
        self._padding       = [16, 16, 16, 16]
        self._shadow        = True
        self._shadow_color  = "rgba(0,0,0,0.08)"
        self._shadow_radius = 8
        self._shadow_offset = [0, 2]

    def shadow(self, value=True):
        self._shadow = value
        return self

    def shadow_color(self, color):
        self._shadow_color = color
        return self

    def to_dict(self):
        d = super().to_dict()
        d["shadow"]        = self._shadow
        d["shadow_color"]  = self._shadow_color
        d["shadow_radius"] = self._shadow_radius
        d["shadow_offset"] = self._shadow_offset
        return d


class Skeleton(Component):
    """
    Loading placeholder that animates.
    Shows while content is being fetched.

    Usage:
        Skeleton().width(200).height(20)
        Skeleton().width(150).height(20)
    """

    def __init__(self):
        super().__init__()
        self._background = "#E5E5EA"
        self._animated   = True

    def to_dict(self):
        d = super().to_dict()
        d["animated"] = self._animated
        return d


class Modal(Component):
    """
    Full screen overlay modal.

    Usage:
        Modal(
            VStack(
                Heading("Are you sure?"),
                Button("Confirm").on_tap(self.confirm),
                Button("Cancel").on_tap(self.dismiss)
            ),
            visible=self.show_modal
        )
    """

    def __init__(self, *children, visible=False):
        super().__init__(*children)
        self._modal_visible = visible
        self._dismissable   = True
        self._background    = "#FFFFFF"
        self._corner_radius = 20

    def dismissable(self, value=True):
        self._dismissable = value
        return self

    def to_dict(self):
        d = super().to_dict()
        d["modal_visible"] = self._modal_visible
        d["dismissable"]   = self._dismissable
        return d


class BottomSheet(Component):
    """
    Sheet that slides up from the bottom.

    Usage:
        BottomSheet(
            VStack(
                Text("Options"),
                Button("Share").on_tap(self.share),
            ),
            visible=self.show_sheet
        )
    """

    def __init__(self, *children, visible=False):
        super().__init__(*children)
        self._sheet_visible = visible
        self._detents       = ["medium", "large"]  # snap points
        self._background    = "#FFFFFF"
        self._corner_radius = 20

    def detents(self, *values):
        self._detents = list(values)
        return self

    def to_dict(self):
        d = super().to_dict()
        d["sheet_visible"] = self._sheet_visible
        d["detents"]       = self._detents
        return d