<div align="center">

# BlinkUI

### The Python-native mobile framework. Write Python. Ship native C.

[![PyPI](https://img.shields.io/pypi/v/blinkui?color=00FF88&label=PyPI)](https://pypi.org/project/blinkui/)
[![License](https://img.shields.io/badge/license-MIT-00FF88)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS-00FF88)](https://feranmi1295.github.io/blinkui)

</div>

---

## What is BlinkUI?

BlinkUI is the only mobile framework that **transpiles Python to native C at build time**.

No JavaScript runtime. No Dart VM. No interpreter on device.  
Write Python → BlinkUI compiles it → Ship pure ARM64 native code.
```python
from blinkui import Screen, state
from blinkui.components import VStack, Text, Button, Card, Heading

class HomeScreen(Screen):
    count = state(0)
    name  = state("World")

    def build(self):
        return VStack(
            Card(
                Heading(f"Hello, {self.name}!"),
                Text("Built with Python and C"),
            ),
            Text(f"Count: {self.count}").size(48).bold().center(),
            Button("Tap Me").on_tap(self.increment),
            Text("Loading...") if self.loading else Text("Ready"),
        ).spacing(16).padding(16)

    def increment(self):
        self.count += 1
```

---

## Why BlinkUI?

| | BlinkUI | React Native | Flutter |
|---|---|---|---|
| Language | **Python** | JavaScript | Dart |
| Runtime on device | **None (pure C)** | Hermes JS engine | Dart VM |
| APK overhead | **~0MB** | ~8MB | ~5MB |
| AI/ML ecosystem | **✅ Native Python** | ❌ | ❌ |
| Transpiler | **✅ Python → C** | ❌ | ❌ |
| Dark theme built-in | **✅** | Manual | Manual |

---

## Install
```bash
pip install blinkui
```

## Quick start
```bash
blink new myapp
cd myapp
blink run
```

## Build for Android
```bash
blink build android
```

Transpiles all Python screens to C, compiles with NDK, produces APK.

---

## Architecture
```
Developer writes Python
        ↓
BlinkUI Transpiler (Python → C)
        ↓
NDK Compiler (C → ARM64)
        ↓
Pure native APK — no interpreter, no bridge, no overhead
```

**Transpiler pipeline:**
- **Parser** — reads Python AST
- **Type inferrer** — `int`, `char`, `float`, `bool` from defaults
- **Code generator** — C structs + event handlers
- **JSON serializer** — runtime component trees with conditionals
- **Store analyzer** — global state as shared C struct

---

## Components

| Layout | Text | Input | Media | Navigation |
|--------|------|-------|-------|------------|
| VStack | Text | Button | Image | NavigationBar |
| HStack | Heading | TextField | Avatar | TabBar |
| Card | Label | Toggle | Icon | Modal |
| ScrollView | Divider | Slider | | ListItem |
| ZStack | Spacer | | | |

---

## State
```python
# Local state — per screen
count = state(0)
name  = state("John")

# Global store — shared across all screens
from blinkui import store
cart_count = store(0)
user       = store({"name": "", "logged_in": False})
```

---

## Navigation
```python
# Stack navigation
def go_detail(self):
    self.navigate("detail", data={"id": self.item_id})

def go_back(self):
    self._navigator.pop()
```

---

## Conditional UI
```python
def build(self):
    return VStack(
        Text("Loading...") if self.loading else Text(f"Count: {self.count}"),
        Button("Retry") if self.error else Button("Continue"),
    )
```

---

## Network
```python
def on_mount(self):
    self.fetch("https://api.example.com/data")

def on_response(self, data):
    self.items = data["items"]
```

---

## Animations

BlinkUI includes a built-in animation system:
- **Fade in/out** — screen transitions
- **Slide in/out** — navigation transitions  
- **Spring bounce** — button press feedback
- **State pulse** — count/value changes

---

## Hot Reload
```bash
blink run --hot
```

Edit Python on laptop → changes appear on device instantly over WiFi.  
No rebuild. No reinstall.

---

## Theme System
```python
from blinkui.theme import dark_theme, light_theme, ocean_theme, ember_theme

# BlinkUI default: dark + electric green
# background: #0F0F0F  accent: #00FF88

set_theme(ocean_theme())   # deep blue
set_theme(ember_theme())   # warm orange
set_theme(light_theme())   # light mode
```

---

## CLI
```bash
blink new myapp          # create new app
blink run                # run on simulator
blink run --hot          # hot reload over WiFi
blink install pandas     # install Python package
blink build android      # transpile + compile APK
blink build ios          # coming soon
```

---

## Roadmap

- [x] Python → C transpiler
- [x] Android bridge (JNI)
- [x] Dark theme + identity
- [x] State management (local + global)
- [x] Navigation (stack + tabs)
- [x] Animations
- [x] TextField + forms
- [x] Image + Avatar
- [x] Modal / Dialog
- [x] Toast notifications
- [x] Hot reload
- [x] Network requests
- [ ] AI-native components (`SmartList`, `AutoStyle`, `AICard`)
- [ ] iOS bridge
- [ ] Web target
- [ ] Plugin ecosystem

---

## Links

- **PyPI:** https://pypi.org/project/blinkui/
- **Docs:** https://feranmi1295.github.io/blinkui
- **GitHub:** https://github.com/feranmi1295/blinkui

---

<div align="center">
Built from scratch in Lagos. 🇳🇬
</div>
