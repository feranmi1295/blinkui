import os
import sys
import subprocess
import threading


def run_command(args):
    hot    = '--hot' in args
    device = '--device' in args

    print("""
╔══════════════════════════════════════════╗
║           BlinkUI CLI v0.1.0             ║
║   Build mobile apps in pure Python       ║
╚══════════════════════════════════════════╝""")

    if not os.path.exists('main.py'):
        print("✗ No BlinkUI app found. Run 'blink new <appname>' first.")
        return

    if hot:
        print("🔥 Hot reload enabled")
        _start_hot_reload()

    if device:
        print("📱 Running on connected device...")
    else:
        print("🚀 Running app...")

    # add .blink/packages to path
    blink_packages = os.path.join(os.getcwd(), '.blink', 'packages')
    if os.path.exists(blink_packages):
        sys.path.insert(0, blink_packages)

    # run the app
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"✗ Error running app: {e}")


def _start_hot_reload():
    try:
        from blinkui.hotreload.server import HotReloadServer
        project_dir = os.getcwd()
        server = HotReloadServer(project_dir)
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        print(f"🔥 Hot reload server listening on port 8974")
        print(f"   Connect your device to the same WiFi network")
    except Exception as e:
        print(f"⚠ Hot reload unavailable: {e}")
