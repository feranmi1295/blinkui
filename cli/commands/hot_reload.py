"""
BlinkUI Hot Reload Server

Watches Python screen files for changes.
On change: transpiles to JSON and pushes to device over TCP.

Usage:
    blink run --hot
    blink run --hot --port 8974
"""

import os
import sys
import time
import socket
import threading
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../transpiler'))

from parser import BlinkUIParser
from type_inferrer import TypeInferrer
from json_serializer import JSONSerializerGenerator

HOT_RELOAD_PORT = 8974
WATCH_INTERVAL  = 0.5  # seconds


class HotReloadServer:

    def __init__(self, project_dir: str, port: int = HOT_RELOAD_PORT):
        self.project_dir  = project_dir
        self.port         = port
        self.clients      = []
        self.file_mtimes  = {}
        self.running      = False
        self.server_sock  = None

    def start(self):
        self.running = True

        # start TCP server
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

        print(f"\n⚡ BlinkUI Hot Reload")
        print(f"   Watching: {self.project_dir}")
        print(f"   Port:     {self.port}")
        print(f"   Waiting for device connection...")
        print(f"\n   On your device: open BlinkUI app")
        print(f"   Make sure device is on same WiFi\n")

        # start file watcher
        self._watch_files()

    def _run_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', self.port))
        self.server_sock.listen(5)

        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                self.clients.append(client_sock)
                print(f"   📱 Device connected: {addr[0]}")
                # send initial screen immediately
                self._send_all_screens()
            except Exception:
                break

    def _watch_files(self):
        screens_dir = os.path.join(self.project_dir, "screens")
        if not os.path.exists(screens_dir):
            print(f"   No screens/ directory found in {self.project_dir}")
            return

        print(f"   Watching screens/...")

        while self.running:
            for fname in os.listdir(screens_dir):
                if not fname.endswith('.py'):
                    continue

                fpath = os.path.join(screens_dir, fname)
                mtime = os.path.getmtime(fpath)

                if fname not in self.file_mtimes:
                    self.file_mtimes[fname] = mtime
                    continue

                if mtime != self.file_mtimes[fname]:
                    self.file_mtimes[fname] = mtime
                    print(f"\n   🔄 Changed: {fname}")
                    self._reload_screen(fpath)

            time.sleep(WATCH_INTERVAL)

    def _reload_screen(self, filepath: str):
        try:
            parser   = BlinkUIParser()
            screen   = parser.parse_file(filepath)
            inferrer = TypeInferrer()
            screen   = inferrer.infer(screen)
            gen      = JSONSerializerGenerator()

            # get initial tree as JSON by running the serializer
            # For hot reload we need the JSON tree directly
            tree_json = self._get_tree_json(screen, gen)

            payload = json.dumps({
                "type":   "screen_update",
                "screen": screen.name,
                "tree":   tree_json
            })

            self._broadcast(payload)
            print(f"   ✅ Sent {screen.name} ({len(payload)} bytes)")

        except Exception as e:
            print(f"   ❌ Transpile error: {e}")
            import traceback
            traceback.print_exc()

    def _get_tree_json(self, screen, gen) -> dict:
        """Build the component tree as a Python dict for JSON encoding."""
        import ast

        if not screen.build_tree:
            return {"type": "VStack", "children": []}

        ret_node = None
        for stmt in screen.build_tree.body:
            if isinstance(stmt, ast.Return):
                ret_node = stmt.value
                break

        if not ret_node:
            return {"type": "VStack", "children": []}

        return self._node_to_dict(ret_node, screen, gen, [0])

    def _node_to_dict(self, node, screen, gen, counter) -> dict:
        import ast
        from json_serializer import extract_chain
        from codegen import COMPONENT_MAP

        if isinstance(node, ast.IfExp):
            # return the 'else' branch for hot reload preview
            return self._node_to_dict(node.orelse, screen, gen, counter)

        if not isinstance(node, ast.Call):
            return {"type": "Text", "content": "?", "children": []}

        base, chain_props = extract_chain(node)
        if not isinstance(base, ast.Call):
            return {"type": "Text", "content": "?", "children": []}

        func_name = gen._get_func_name(base)
        if func_name not in COMPONENT_MAP:
            return {"type": "Text", "content": "?", "children": []}

        counter[0] += 1
        node_id = counter[0] + 100

        styling  = gen._build_styling(func_name, chain_props, node_id)
        result   = {"type": func_name, "node_id": node_id, **styling}

        # content
        if base.args:
            arg = base.args[0]
            if isinstance(arg, ast.Constant):
                key = "label" if func_name == "Button" else "content"
                result[key] = str(arg.value)
            elif isinstance(arg, ast.JoinedStr):
                key = "label" if func_name == "Button" else "content"
                result[key] = f"[dynamic]"

        # keyword title
        for kw in base.keywords:
            if kw.arg == "title" and isinstance(kw.value, ast.Constant):
                result["content"] = kw.value.value

        # children
        children = []
        for arg in base.args:
            if isinstance(arg, ast.Call):
                b, _ = extract_chain(arg)
                if isinstance(b, ast.Call):
                    fname = gen._get_func_name(b)
                    if fname in COMPONENT_MAP:
                        children.append(
                            self._node_to_dict(arg, screen, gen, counter)
                        )
        result["children"] = children

        return result

    def _send_all_screens(self):
        screens_dir = os.path.join(self.project_dir, "screens")
        if not os.path.exists(screens_dir):
            return
        for fname in os.listdir(screens_dir):
            if fname.endswith('.py'):
                self._reload_screen(os.path.join(screens_dir, fname))

    def _broadcast(self, message: str):
        dead = []
        msg_bytes = (message + "\n").encode('utf-8')
        for client in self.clients:
            try:
                client.sendall(msg_bytes)
            except Exception:
                dead.append(client)
        for d in dead:
            self.clients.remove(d)

    def stop(self):
        self.running = False
        if self.server_sock:
            self.server_sock.close()


def run_hot_reload(project_dir: str, port: int = HOT_RELOAD_PORT):
    server = HotReloadServer(project_dir, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n   Hot reload stopped.")
        server.stop()
