# ─────────────────────────────────────────
# HTTP Response object
# What every request returns
# ─────────────────────────────────────────

import json as _json


class Response:
    """
    Returned from every HTTP request.

    Attributes:
        ok      — True if status 200-299
        status  — HTTP status code
        data    — parsed JSON response body
        text    — raw response as string
        error   — error message if request failed
        headers — response headers
    """

    def __init__(
        self,
        status:  int  = 0,
        data          = None,
        text:    str  = "",
        error:   str  = None,
        headers: dict = None,
    ):
        self.status  = status
        self.data    = data
        self.text    = text
        self.error   = error
        self.headers = headers or {}

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def is_error(self) -> bool:
        return self.error is not None or self.status >= 400

    def json(self):
        """Parse text as JSON if data not already parsed."""
        if self.data is not None:
            return self.data
        try:
            return _json.loads(self.text)
        except Exception:
            return None

    def __repr__(self):
        return f"<Response status={self.status} ok={self.ok}>"