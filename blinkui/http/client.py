# ─────────────────────────────────────────
# BlinkUI HTTP client
# Async HTTP requests that never freeze UI
# ─────────────────────────────────────────

import asyncio
import json as _json
import urllib.request
import urllib.error
import urllib.parse
from .response import Response


# ─────────────────────────────────────────
# Default headers sent with every request
# ─────────────────────────────────────────
_DEFAULT_HEADERS = {
    "Content-Type":  "application/json",
    "Accept":        "application/json",
    "User-Agent":    "BlinkUI/1.0",
}

# global base URL — set once, used everywhere
_base_url = ""

# global default headers — merged with per-request headers
_global_headers = {}


def set_base_url(url: str):
    """
    Set a base URL for all requests.

    Usage:
        from blinkui.http import set_base_url
        set_base_url("https://api.myapp.com")

        # now you can use relative paths
        response = await get("/users")
    """
    global _base_url
    _base_url = url.rstrip("/")


def set_headers(headers: dict):
    """
    Set default headers sent with every request.

    Usage:
        from blinkui.http import set_headers
        set_headers({"Authorization": "Bearer mytoken"})
    """
    global _global_headers
    _global_headers.update(headers)


def set_token(token: str, scheme: str = "Bearer"):
    """
    Shortcut to set Authorization header.

    Usage:
        from blinkui.http import set_token
        set_token("my_jwt_token")
    """
    set_headers({"Authorization": f"{scheme} {token}"})


# ─────────────────────────────────────────
# Internal request executor
# Runs in a thread so it never blocks UI
# ─────────────────────────────────────────
def _build_url(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{_base_url}/{url.lstrip('/')}"


def _build_headers(extra: dict = None) -> dict:
    headers = dict(_DEFAULT_HEADERS)
    headers.update(_global_headers)
    if extra:
        headers.update(extra)
    return headers


def _execute_request(
    method:  str,
    url:     str,
    body:    dict = None,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    """Runs synchronously in a thread pool."""
    full_url = _build_url(url)
    hdrs     = _build_headers(headers)

    try:
        data = None
        if body is not None:
            data = _json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            full_url,
            data=data,
            headers=hdrs,
            method=method.upper(),
        )

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_text = resp.read().decode("utf-8")
            status   = resp.status
            resp_headers = dict(resp.headers)

            # try to parse JSON
            parsed = None
            try:
                parsed = _json.loads(raw_text)
            except Exception:
                pass

            return Response(
                status  = status,
                data    = parsed,
                text    = raw_text,
                headers = resp_headers,
            )

    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8") if e.fp else ""
        parsed = None
        try:
            parsed = _json.loads(raw)
        except Exception:
            pass

        return Response(
            status = e.code,
            data   = parsed,
            text   = raw,
            error  = f"HTTP {e.code}: {e.reason}",
        )

    except urllib.error.URLError as e:
        return Response(
            status = 0,
            error  = f"Connection error: {e.reason}",
        )

    except Exception as e:
        return Response(
            status = 0,
            error  = f"Request failed: {str(e)}",
        )


# ─────────────────────────────────────────
# Async wrappers
# These run the sync request in a thread
# so the UI event loop stays free
# ─────────────────────────────────────────

async def _async_request(
    method:  str,
    url:     str,
    body:    dict = None,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: _execute_request(method, url, body, headers, timeout)
    )


async def get(
    url:     str,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    """
    Async GET request.

    Usage:
        response = await get("https://api.example.com/users")
        if response.ok:
            self.users = response.data
        else:
            self.error = response.error
    """
    print(f"[HTTP] GET {url}")
    response = await _async_request("GET", url, headers=headers, timeout=timeout)
    print(f"[HTTP] GET {url} → {response.status}")
    return response


async def post(
    url:     str,
    body:    dict = None,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    """
    Async POST request.

    Usage:
        response = await post("/users", {"name": "John"})
        if response.ok:
            self.navigate("success")
    """
    print(f"[HTTP] POST {url}")
    response = await _async_request("POST", url, body, headers, timeout)
    print(f"[HTTP] POST {url} → {response.status}")
    return response


async def put(
    url:     str,
    body:    dict = None,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    """
    Async PUT request.

    Usage:
        response = await put("/users/42", {"name": "Updated"})
    """
    print(f"[HTTP] PUT {url}")
    response = await _async_request("PUT", url, body, headers, timeout)
    print(f"[HTTP] PUT {url} → {response.status}")
    return response


async def patch(
    url:     str,
    body:    dict = None,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    """
    Async PATCH request.

    Usage:
        response = await patch("/users/42", {"email": "new@email.com"})
    """
    print(f"[HTTP] PATCH {url}")
    response = await _async_request("PATCH", url, body, headers, timeout)
    print(f"[HTTP] PATCH {url} → {response.status}")
    return response


async def delete(
    url:     str,
    headers: dict = None,
    timeout: int  = 30,
) -> Response:
    """
    Async DELETE request.

    Usage:
        response = await delete("/users/42")
        if response.ok:
            self.navigate("home")
    """
    print(f"[HTTP] DELETE {url}")
    response = await _async_request("DELETE", url, headers=headers, timeout=timeout)
    print(f"[HTTP] DELETE {url} → {response.status}")
    return response