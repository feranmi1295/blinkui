# Getting Started

## Install BlinkUI
```bash
pip install blinkui
```

## Create your first app
```bash
blink new myapp
cd myapp
blink run
```

Your app is running. Open `screens/home.py` to start editing.

---

## Project structure
```
myapp/
├── main.py              # entry point
├── blink.toml           # project config
├── screens/
│   ├── home.py          # home screen
│   └── detail.py        # detail screen
├── components/          # your custom components
└── assets/
    └── images/
```

---

## Your first screen

Every screen inherits from `Screen` and implements `build()`:
```python
from blinkui import Screen, state
from blinkui.components import VStack, Text, Button, Heading

class HomeScreen(Screen):
    count = state(0)

    def build(self):
        return VStack(
            Heading("My First App"),
            Text(f"Count: {self.count}").size(32).bold(),
            Button("Tap Me").on_tap(self.increment),
        ).spacing(16).padding(24)

    def increment(self):
        self.count += 1

    def on_mount(self):
        print("Screen mounted")
```

---

## Entry point

`main.py` sets up routing and launches the app:
```python
from blinkui import Router
from screens.home import HomeScreen
from screens.detail import DetailScreen

Router(
    routes={
        "home":   HomeScreen,
        "detail": DetailScreen,
    },
    entry="home"
)
```

---

## CLI commands
```bash
blink new myapp          # create a new app
blink run                # run on simulator
blink run --hot          # hot reload on save
blink run --device       # run on connected device
blink install pandas     # install Python packages
blink build ios          # build for App Store
blink build android      # build for Play Store
```

---

## Installing packages
```bash
blink install requests
blink install pandas
blink install numpy
```

Packages install into `.blink/packages/` and are bundled with your app at build time.
```python
# use them normally in your screens
import requests
import pandas as pd
```