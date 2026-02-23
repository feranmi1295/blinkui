#!/usr/bin/env python3
# ─────────────────────────────────────────
# BlinkUI CLI — blink command
# ─────────────────────────────────────────

import sys
from cli.commands.new     import cmd_new
from cli.commands.run     import cmd_run
from cli.commands.build   import cmd_build
from cli.commands.install import cmd_install

HELP = """
╔══════════════════════════════════════════╗
║           BlinkUI CLI v0.1.0             ║
║   Build mobile apps in pure Python       ║
╚══════════════════════════════════════════╝

Usage:
  blink new <appname>        Create a new BlinkUI app
  blink run                  Run app on simulator
  blink run --hot            Run with hot reload
  blink run --device         Run on connected device
  blink build ios            Build for App Store
  blink build android        Build for Play Store
  blink install <package>    Install a Python package
  blink --help               Show this help

Examples:
  blink new myapp
  blink run --hot
  blink install pandas
  blink build android
"""

def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h", "help"):
        print(HELP)
        return

    command = args[0]
    rest    = args[1:]

    if command == "new":
        if not rest:
            print("[blink] Error: please provide an app name.")
            print("  Usage: blink new <appname>")
            return
        cmd_new(rest[0])

    elif command == "run":
        hot    = "--hot"    in rest
        device = "--device" in rest
        cmd_run(hot=hot, device=device)

    elif command == "build":
        if not rest:
            print("[blink] Error: please specify platform.")
            print("  Usage: blink build ios")
            print("  Usage: blink build android")
            return
        cmd_build(rest[0])

    elif command == "install":
        if not rest:
            print("[blink] Error: please specify a package.")
            print("  Usage: blink install pandas")
            return
        cmd_install(rest)

    else:
        print(f"[blink] Unknown command: '{command}'")
        print("  Run 'blink --help' to see available commands.")


if __name__ == "__main__":
    main()