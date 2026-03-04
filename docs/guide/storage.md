# Storage

BlinkUI includes persistent async storage. Data survives app restarts.

## Basic usage
```python
from blinkui.storage import storage

# save
await storage.set("token", "abc123")

# get
token = await storage.get("token")

# get with fallback
theme = await storage.get("theme", default="light")

# delete
await storage.delete("token")

# check exists
if await storage.has("token"):
    self.navigate("dashboard")
else:
    self.navigate("login")
```

## Storing complex data
```python
# dicts and lists are serialized automatically
await storage.set("user", {
    "id":    42,
    "name":  "John",
    "email": "john@example.com"
})

user = await storage.get("user")
print(user["name"])  # John
```

## Batch operations
```python
# save multiple at once
await storage.set_many({
    "token":    "abc123",
    "user_id":  42,
    "theme":    "dark"
})

# get multiple at once
result = await storage.get_many(["token", "user_id", "theme"])
```

## All keys and clear
```python
# get all keys
keys = await storage.keys()

# get everything
everything = await storage.get_all()

# clear all data — useful for logout
await storage.clear()
```

## Common pattern — auth check on mount
```python
class SplashScreen(Screen):
    async def on_mount(self):
        token = await storage.get("token")
        if token:
            self.navigate("home")
        else:
            self.navigate("login")
```