# ─────────────────────────────────────────
# blink run
# Runs the BlinkUI app
# ─────────────────────────────────────────

import os
import sys
import time
from pathlib import Path


def cmd_run(hot: bool = False, device: bool = False):
    print(f"""
╔══════════════════════════════════════════╗
║            BlinkUI Runner                ║
╚══════════════════════════════════════════╝
""")

    # check we are inside a BlinkUI project
    if not Path("blink.toml").exists():
        print("[blink] Error: no blink.toml found.")
        print("  Are you inside a BlinkUI project?")
        print("  Run: blink new myapp")
        return

    if not Path("main.py").exists():
        print("[blink] Error: no main.py found.")
        return

    mode = "device" if device else "simulator"
    reload = "hot reload enabled" if hot else ""

    print(f"[blink] Starting app...")
    print(f"[blink] Mode:   {mode}")
    if hot:
        print(f"[blink] Hot reload: enabled")
        print(f"[blink] Save any file to reload instantly")

    print(f"[blink] Running main.py\n")
    print("─" * 44)

    # add current dir to path so imports work
    sys.path.insert(0, str(Path.cwd()))

    if hot:
        _run_with_hot_reload()
    else:
        _run_once()


def _run_once():
    """Run the app once."""
    try:
        import importlib
        import main
    except Exception as e:
        print(f"\n[blink] Error: {e}")


def _run_with_hot_reload():
    """Watch files and reload on change."""
    import importlib
    import importlib.util

    print("[blink] Watching for file changes...\n")

    # track file modification times
    def get_mtimes():
        mtimes = {}
        for ext in ("*.py",):
            for path in Path(".").rglob(ext):
                try:
                    mtimes[str(path)] = path.stat().st_mtime
                except Exception:
                    pass
        return mtimes

    last_mtimes = get_mtimes()

    # run initially
    try:
        import main
    except Exception as e:
        print(f"[blink] Error: {e}")

    # watch loop
    try:
        while True:
            time.sleep(0.5)
            current_mtimes = get_mtimes()

            changed = [
                f for f, t in current_mtimes.items()
                if last_mtimes.get(f) != t
            ]

            if changed:
                for f in changed:
                    print(f"\n[blink] Changed: {f}")
                print("[blink] Reloading...\n")
                print("─" * 44)

                # reload all changed modules
                mods_to_reload = [
                    name for name, mod in sys.modules.items()
                    if hasattr(mod, "__file__")
                    and mod.__file__
                    and any(f in mod.__file__ for f in changed)
                ]
                for mod_name in mods_to_reload:
                    try:
                        importlib.reload(sys.modules[mod_name])
                    except Exception:
                        pass

                last_mtimes = current_mtimes

    except KeyboardInterrupt:
        print("\n[blink] Stopped.")