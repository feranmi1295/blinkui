# HTTP Client

BlinkUI includes a built in async HTTP client. All requests run in the background so the UI never freezes.

## Basic usage
```python
from blinkui.http import get, post

class HomeScreen(Screen):
    data  = state(None)
    error = state(None)

    async def on_mount(self):
        response = await get("https://api.example.com/users")
        if response.ok:
            self.data = response.data
        else:
            self.error = response.error
```

## POST request
```python
async def create_user(self):
    response = await post("https://api.example.com/users", {
        "name":  "John Doe",
        "email": "john@example.com"
    })
    if response.ok:
        self.navigate("success")
```

## Set base URL
```python
# in main.py — set once, use everywhere
from blinkui.http import set_base_url
set_base_url("https://api.myapp.com")

# now use relative paths anywhere
response = await get("/users")
response = await post("/users", data)
```

## Authentication
```python
from blinkui.http import set_token

# sets Authorization: Bearer <token> on all requests
set_token("my_jwt_token")
```

## All methods
```python
from blinkui.http import get, post, put, patch, delete

response = await get("/users")
response = await post("/users", {"name": "John"})
response = await put("/users/42", {"name": "Updated"})
response = await patch("/users/42", {"email": "new@email.com"})
response = await delete("/users/42")
```

## Response object
```python
response.ok       # True if status 200-299
response.status   # HTTP status code
response.data     # parsed JSON as dict or list
response.text     # raw response string
response.error    # error message if failed
response.headers  # response headers dict
```