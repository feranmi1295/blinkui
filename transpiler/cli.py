"""
BlinkUI Transpiler CLI
Invoked by: blink build android
"""

import os
import sys
import subprocess
import argparse
sys.path.insert(0, os.path.dirname(__file__))

from parser import BlinkUIParser
from type_inferrer import TypeInferrer
from json_serializer import JSONSerializerGenerator
from store_analyzer import find_stores, generate_global_store_h, generate_global_store_c

def transpile_screen(py_file: str, out_dir: str) -> str:
    """Transpile a single Python screen to C."""
    print(f"  Transpiling {os.path.basename(py_file)}...")

    parser   = BlinkUIParser()
    screen   = parser.parse_file(py_file)
    inferrer = TypeInferrer()
    screen   = inferrer.infer(screen)
    gen      = JSONSerializerGenerator()
    c_code   = gen.generate(screen)

    out_file = os.path.join(out_dir, f"{screen.name}.c")
    with open(out_file, "w") as f:
        f.write(c_code)

    print(f"  ✅ {screen.name} → {out_file}")
    return out_file

def find_screens(project_dir: str) -> list:
    """Find all screen files in a BlinkUI project."""
    screens_dir = os.path.join(project_dir, "screens")
    if not os.path.exists(screens_dir):
        return []
    return [
        os.path.join(screens_dir, f)
        for f in os.listdir(screens_dir)
        if f.endswith(".py") and not f.startswith("_")
    ]

def build_android(project_dir: str):
    """Full build pipeline for Android."""
    print("🔨 BlinkUI — Building for Android")
    print(f"   Project: {project_dir}")

    # 1 — find screens
    screens = find_screens(project_dir)
    if not screens:
        # also check main.py
        main = os.path.join(project_dir, "main.py")
        if os.path.exists(main):
            screens = [main]

    if not screens:
        print("❌ No screens found")
        sys.exit(1)

    print(f"\n📄 Found {len(screens)} screen(s)")

    # 2 — create output dir
    out_dir = os.path.join(project_dir, ".blink", "generated", "c")
    os.makedirs(out_dir, exist_ok=True)

    # 3 — analyze and generate global store
    print("\n🗄️  Analyzing global stores")
    stores = find_stores(project_dir)
    if stores:
        print(f"   Found {len(stores)} store(s): {[s.name for s in stores]}")
    generate_global_store_h(stores, out_dir)
    generate_global_store_c(stores, out_dir)

    # 3 — transpile each screen
    print("\n🔄 Transpiling Python → C")
    c_files = []
    for screen_file in screens:
        try:
            c_file = transpile_screen(screen_file, out_dir)
            c_files.append(c_file)
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            sys.exit(1)

    # 4 — compile with NDK
    ndk = os.environ.get("ANDROID_NDK")
    if not ndk:
        print("\n⚠️  ANDROID_NDK not set — skipping native compile")
        print("   Set ANDROID_NDK and run again to compile .so")
    else:
        print(f"\n🔧 Compiling with NDK...")
        compile_with_ndk(c_files, out_dir, ndk, project_dir)

    print(f"\n✅ Build complete")
    print(f"   Generated C: {out_dir}")

def compile_with_ndk(c_files, out_dir, ndk, project_dir):
    """Compile generated C files to ARM64 .so using NDK."""
    clang = os.path.join(
        ndk,
        "toolchains/llvm/prebuilt/linux-x86_64/bin",
        "aarch64-linux-android24-clang"
    )

    runtime = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "runtime"
    )

    output = os.path.join(out_dir, "libblinkui_app.so")

    runtime_sources = [
        os.path.join(runtime, "core/components.c"),
        os.path.join(runtime, "core/reconciler.c"),
        os.path.join(runtime, "core/events.c"),
        os.path.join(runtime, "animation/animation.c"),
    ]

    global_store_c = os.path.join(out_dir, "global_store.c")
    extra = [global_store_c] if os.path.exists(global_store_c) else []

    cmd = [
        clang,
        "-shared", "-fPIC",
        "-DANDROID", "-DNO_PYTHON",
        f"-I{out_dir}",
        "-o", output,
        f"-I{runtime}/core",
        f"-I{runtime}/animation",
    ] + c_files + extra + runtime_sources + ["-llog", "-lm"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size = os.path.getsize(output)
        print(f"  ✅ libblinkui_app.so ({size} bytes)")
    else:
        print(f"  ❌ Compile error:")
        print(result.stderr)

def main():
    parser = argparse.ArgumentParser(description="BlinkUI Transpiler")
    parser.add_argument("command", choices=["android", "inspect"])
    parser.add_argument("--project", default=".", help="Project directory")
    parser.add_argument("--screen", help="Single screen file to transpile")

    args = parser.parse_args()

    if args.command == "android":
        build_android(os.path.abspath(args.project))

    elif args.command == "inspect":
        if not args.screen:
            print("--screen required for inspect")
            sys.exit(1)
        p      = BlinkUIParser()
        screen = p.parse_file(args.screen)
        inf    = TypeInferrer()
        screen = inf.infer(screen)
        print(f"Screen:  {screen.name}")
        print(f"State:   {[(sv.name, sv.inferred_type) for sv in screen.state_vars]}")
        print(f"Handlers:{[h.name for h in screen.event_handlers]}")
        print(f"Build:   {'yes' if screen.build_tree else 'no'}")

if __name__ == "__main__":
    main()
