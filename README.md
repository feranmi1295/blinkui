<div align="center">

# ⚡ BlinkUI

### Build mobile apps in pure Python

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-iOS%20%7C%20Android-lightgrey.svg)]()

</div>

---

## What is BlinkUI?

BlinkUI is a mobile app framework for Python developers. Write your app in pure Python and ship it to iOS and Android. No Swift, no Kotlin, no JavaScript.
```python
from blinkui import Screen, state
from blinkui.components import VStack, Text, Button, Heading

class HomeScreen(Screen):
    count = state(0)

    def build(self):
        return VStack(
            Heading("Hello from BlinkUI"),
            Text(f"Count: {self.count}").size(48).bold(),
            Button("Tap Me").on_tap(self.increment),
        ).spacing(16).padding(24)

    def increment(self):
        self.count += 1
```

---

## Why BlinkUI?

| | BlinkUI | React Native | Flutter |
|---|---|---|---|
| Language | **Python** | JavaScript | Dart |
| Python ecosystem | **✅ Full access** | ❌ | ❌ |
| AI/ML libraries | **✅ pandas, numpy** | ❌ | ❌ |
| Native UI | ✅ | ✅ | ❌ |
| Hot reload | ✅ | ✅ | ✅ |

---

## Getting started
```bash
pip install blinkui
blink new myapp
cd myapp
blink run
```

---

## Architecture

BlinkUI is built in two layers:

**C Runtime** — a fast native engine inspired by Facebook's Hermes:
- Node tree — every UI element represented in memory
- Reconciler — diffs component trees, patches only what changed
- Event system — catches native interactions, fires Python callbacks
- Animation engine — 60fps animations running entirely in C
- CPython host — embeds Python inside iOS and Android

**Python Framework** — what developers write in:
- `state()` — declare reactive variables, UI updates automatically
- `Screen` — base class for every screen
- `Router` — navigation stack with data passing
- `Theme` — iOS-inspired design system with dark mode
- HTTP client — async requests that never freeze the UI
- Async storage — persistent key-value storage

---

## Components
```python
from blinkui.components import (
    # Layout
    VStack, HStack, ZStack, ScrollView, Spacer,

    # Text
    Text, Heading, Label, Badge,

    # Input
    Button, TextField, Toggle, Slider,

    # Display
    Card, Image, Avatar, Modal, BottomSheet,

    # Navigation
    TabBar, NavigationBar, Toast,
)
```

---

## HTTP and AI backend

BlinkUI apps connect to Python backends via HTTP:
```python
from blinkui.http import get, post, set_base_url, set_token

class DashboardScreen(Screen):
    data = state(None)

    async def on_mount(self):
        response = await get("https://api.myapp.com/data")
        if response.ok:
            self.data = response.data
        else:
            self.error = response.error
```

Your AI and ML code lives on the server — pandas, tensorflow, pytorch — and your BlinkUI app calls it via API. Mobile stays fast. Python stays powerful.

---

## Storage
```python
from blinkui.storage import storage

# save
await storage.set("token", "abc123")

# get
token = await storage.get("token")

# delete
await storage.delete("token")
```

---

## CLI
```bash
blink new myapp          # create a new app
blink run                # run on simulator
blink run --hot          # hot reload
blink install pandas     # install packages
blink build ios          # build for App Store
blink build android      # build for Play Store
```

---

## Project structure
```
myapp/
├── main.py              # entry point
├── blink.toml           # project config
├── screens/
│   ├── home.py
│   └── detail.py
├── components/
└── assets/
```

---

## Roadmap

- [x] C runtime — node tree, reconciler, events, animations
- [x] CPython embedding on mobile
- [x] Python framework — state, screen, router, theme
- [x] Component library
- [x] HTTP client
- [x] Async storage
- [x] CLI tool
- [ ] Android native bridge
- [ ] Hot reload on device
- [ ] PyPI publish
- [ ] iOS bridge
- [ ] Documentation site

---

## License

MIT — free to use, modify, and distribute.

---

<div align="center">
Built with Python and C by the BlinkUI team
</div>
test
