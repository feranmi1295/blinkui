# BlinkUI

<div align="center">
<h3>Build mobile apps in pure Python</h3>
</div>

---

## What is BlinkUI?

BlinkUI is a mobile app framework that lets Python developers build iOS and Android apps without learning Swift, Kotlin, or JavaScript.

Write your app in pure Python. BlinkUI's C runtime handles rendering, animations, and events natively on device.
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
| Python ecosystem | **✅ Full** | ❌ | ❌ |
| AI/ML integration | **✅ Via API** | ❌ | ❌ |
| Native UI | ✅ | ✅ | ❌ |
| Learning curve | **Low** | Medium | High |

---

## Install
```bash
pip install blinkui
```

---

## Quick start
```bash
pip install blinkui
blink new myapp
cd myapp
blink run
```

---

## Architecture

BlinkUI is built in two layers:

**C Runtime** — inspired by Facebook's Hermes engine:

- Node tree — every UI element in memory
- Reconciler — diffs trees, patches only what changed
- Event system — native interactions call Python callbacks
- Animation engine — 60fps running entirely in C
- CPython host — Python embedded inside iOS and Android

**Python Framework** — what developers write in:

- `state()` — reactive variables, UI updates automatically
- `Screen` — base class for every screen
- `Router` — navigation with data passing
- `Theme` — iOS-inspired design system
- HTTP client — async requests, never freezes UI
- Async storage — persistent key-value store

---

## Next steps

- [Getting Started](guide/getting-started.md) — build your first app
- [State Management](guide/state.md) — reactive state
- [Navigation](guide/navigation.md) — move between screens
- [Components](components/layout.md) — full component reference