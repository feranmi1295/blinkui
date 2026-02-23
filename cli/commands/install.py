# ─────────────────────────────────────────
# blink install <package>
# Installs Python packages into .blink/packages
# ─────────────────────────────────────────

import subprocess
import sys
from pathlib import Path


def cmd_install(packages: list):
    print(f"""
╔══════════════════════════════════════════╗
║         BlinkUI Package Manager          ║
╚══════════════════════════════════════════╝
""")

    if not Path("blink.toml").exists():
        print("[blink] Error: no blink.toml found.")
        print("  Are you inside a BlinkUI project?")
        return

    # ensure .blink/packages exists
    packages_dir = Path(".blink") / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)

    for package in packages:
        _install_package(package, packages_dir)

    # update blink.toml with installed packages
    _update_toml(packages)

    print(f"\n[blink] ✅ Done. Packages ready to use.")
    print(f"[blink] Import them normally in your screens:")
    for pkg in packages:
        name = pkg.split("==")[0]
        print(f"  import {name}")


def _install_package(package: str, target_dir: Path):
    print(f"[blink] Installing {package}...")

    result = subprocess.run(
        [
            sys.executable, "-m", "pip", "install",
            package,
            "--target", str(target_dir),
            "--quiet",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"[blink] ✅ {package} installed")
    else:
        print(f"[blink] ❌ Failed to install {package}")
        if result.stderr:
            print(f"  {result.stderr.strip()}")


def _update_toml(packages: list):
    """Add installed packages to blink.toml."""
    toml_path = Path("blink.toml")
    if not toml_path.exists():
        return

    content = toml_path.read_text()

    for package in packages:
        name    = package.split("==")[0]
        version = package.split("==")[1] if "==" in package else "latest"

        entry = f'{name} = "{version}"'

        if name not in content:
            content = content.replace(
                "# pandas = \"2.1.0\"",
                f"# pandas = \"2.1.0\"\n{entry}"
            )

    toml_path.write_text(content)