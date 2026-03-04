# Navigation

BlinkUI uses a stack based router. Screens push onto the stack and pop off when going back.

## Setup
```python
from blinkui import Router
from screens.home import HomeScreen
from screens.profile import ProfileScreen
from screens.settings import SettingsScreen

Router(
    routes={
        "home":     HomeScreen,
        "profile":  ProfileScreen,
        "settings": SettingsScreen,
    },
    entry="home"
)
```

## Navigate forward
```python
def go_profile(self):
    self.navigate("profile")
```

## Pass data between screens
```python
def go_profile(self):
    self.navigate("profile", data={
        "user_id": 42,
        "name": "John"
    })
```

Receive it in the next screen:
```python
class ProfileScreen(Screen):
    def build(self):
        user_id = self.route_data.get("user_id")
        name    = self.route_data.get("name")
        return VStack(
            Text(f"Profile: {name}"),
        )
```

## Go back
```python
def go_back(self):
    self._navigator.pop()
```

## Replace current screen
```python
# replaces current screen without adding to stack
def go_login(self):
    self._navigator.replace("login")
```

## Reset stack
```python
# clear entire stack and start fresh
def logout(self):
    self._navigator.reset("login")
```

## Lifecycle hooks
```python
class HomeScreen(Screen):
    def on_mount(self):
        # called when screen appears
        print("mounted")

    def on_unmount(self):
        # called when screen is removed
        print("unmounted")
```