# ─────────────────────────────────────────
# blink new <appname>
# Scaffolds a new BlinkUI project
# ─────────────────────────────────────────

import os
import json
from pathlib import Path


def cmd_new(app_name: str):
    print(f"""
╔══════════════════════════════════════════╗
║         Creating BlinkUI App             ║
╚══════════════════════════════════════════╝
""")

    target = Path.cwd() / app_name

    if target.exists():
        print(f"[blink] Error: '{app_name}' already exists.")
        return

    print(f"[blink] Scaffolding '{app_name}'...")

    # ── create folder structure ──
    folders = [
        target,
        target / "screens",
        target / "components",
        target / "assets",
        target / "assets" / "images",
        target / ".blink",
        target / ".blink" / "packages",
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    # ── blink.toml ──
    blink_toml = f"""[app]
name        = "{app_name}"
version     = "1.0.0"
description = "A BlinkUI app"
author      = ""

[build]
entry       = "main.py"
bundle_id   = "com.example.{app_name.lower()}"

[dependencies]
# Add Python packages here
# Example:
# pandas = "2.1.0"
# requests = "2.31.0"
"""
    _write(target / "blink.toml", blink_toml)

    # ── .gitignore ──
    gitignore = """.blink/
__pycache__/
*.pyc
*.pyo
.env
build/
dist/
"""
    _write(target / ".gitignore", gitignore)

    # ── main.py ──
    main_py = f"""from blinkui import App, Router
from screens.home import HomeScreen
from screens.detail import DetailScreen

Router(
    routes={{
        "home":   HomeScreen,
        "detail": DetailScreen,
    }},
    entry="home"
)
"""
    _write(target / "main.py", main_py)

    # ── screens/home.py ──
    home_py = """from blinkui import Screen, state
from blinkui.components import (
    VStack, HStack, Text, Heading,
    Label, Button, Card, NavigationBar
)


class HomeScreen(Screen):
    count = state(0)

    def build(self):
        return VStack(
            NavigationBar(title="Home"),

            Card(
                VStack(
                    Heading("Welcome to BlinkUI"),
                    Label("Build mobile apps in pure Python"),
                ).spacing(8)
            ),

            Text(f"Count: {self.count}").size(32).bold().center(),

            HStack(
                Button("Increment").on_tap(self.increment),
                Button("Reset").background("#FF3B30").on_tap(self.reset),
            ).spacing(12),

            Button("Go to Detail").on_tap(self.go_detail),

        ).spacing(16).padding(16)

    def increment(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def go_detail(self):
        self.navigate("detail", data={"count": self.count})

    def on_mount(self):
        print("[HomeScreen] mounted")
"""
    _write(target / "screens" / "home.py", home_py)

    # ── screens/detail.py ──
    detail_py = """from blinkui import Screen
from blinkui.components import VStack, Heading, Text, Button, NavigationBar


class DetailScreen(Screen):
    def build(self):
        count = getattr(self, "_route_data", {}).get("count", 0)
        return VStack(
            NavigationBar(title="Detail"),
            Heading("Detail Screen"),
            Text(f"You passed count: {count}"),
            Button("Go Back").on_tap(self.go_back),
        ).spacing(16).padding(16)

    def go_back(self):
        self._navigator.pop()

    def on_mount(self):
        print("[DetailScreen] mounted")
"""
    _write(target / "screens" / "detail.py", detail_py)

    # ── screens/__init__.py ──
    _write(target / "screens" / "__init__.py", "")

    # ── components/__init__.py ──
    _write(target / "components" / "__init__.py", "")

    # ── README.md ──
    readme = f"""# {app_name}

A BlinkUI mobile app.

## Getting started
```bash
cd {app_name}
blink run
```

## Commands
```bash
blink run              # run on simulator
blink run --hot        # hot reload
blink install pandas   # install a package
blink build ios        # build for App Store
blink build android    # build for Play Store
```
"""
    _write(target / "README.md", readme)

    # ── success output ──
    print(f"""
[blink] ✅ Created '{app_name}' successfully!

Project structure:
  {app_name}/
  ├── main.py           ← entry point
  ├── blink.toml        ← project config
  ├── screens/
  │   ├── home.py
  │   └── detail.py
  ├── components/
  └── assets/

Next steps:
  cd {app_name}
  blink run
""")


def _write(path: Path, content: str):
    with open(path, "w") as f:
        f.write(content)
    print(f"  created: {path.name}")