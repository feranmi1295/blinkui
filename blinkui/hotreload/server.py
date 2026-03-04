"""
BlinkUI Hot Reload Server
Watches Python files for changes and pushes updates to the device over WiFi.
"""

import socket
import json
import time
import hashlib
import threading
from pathlib import Path


class HotReloadServer:
    PORT = 8974

    def __init__(self, project_dir: str):
        self.project_dir  = Path(project_dir)
        self.clients      = []
        self.file_hashes  = {}
        self.running      = False

    def start(self):
        self.running = True

        # start TCP server
        server_thread = threading.Thread(target=self._serve, daemon=True)
        server_thread.start()

        # start file watcher
        print(f"[BlinkUI] Hot reload server started on port {self.PORT}")
        print(f"[BlinkUI] Watching: {self.project_dir}")
        print(f"[BlinkUI] Waiting for device to connect...")
        self._watch()

    def _serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.PORT))
        sock.listen(5)

        while self.running:
            try:
                conn, addr = sock.accept()
                print(f"[BlinkUI] Device connected: {addr[0]}")
                self.clients.append(conn)
                threading.Thread(
                    target=self._handle_client,
                    args=(conn,),
                    daemon=True
                ).start()
            except Exception as e:
                pass

    def _handle_client(self, conn):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get('type') == 'ping':
                    conn.send(json.dumps({'type': 'pong'}).encode())
        except:
            pass
        finally:
            if conn in self.clients:
                self.clients.remove(conn)
            print(f"[BlinkUI] Device disconnected")

    def _watch(self):
        # take initial snapshot
        self._snapshot()

        while self.running:
            time.sleep(0.5)
            changed = self._detect_changes()
            if changed:
                for path in changed:
                    print(f"[BlinkUI] Changed: {path}")
                self._push_reload(changed)

    def _snapshot(self):
        for path in self._get_python_files():
            self.file_hashes[path] = self._hash(path)

    def _detect_changes(self):
        changed = []
        for path in self._get_python_files():
            h = self._hash(path)
            if self.file_hashes.get(path) != h:
                self.file_hashes[path] = h
                changed.append(path)
        return changed

    def _push_reload(self, changed_files):
        if not self.clients:
            print("[BlinkUI] No devices connected — save again after connecting")
            return

        # read changed file contents
        files = {}
        for path in changed_files:
            try:
                files[path] = Path(path).read_text()
            except:
                pass

        msg = json.dumps({
            'type':  'reload',
            'files': files,
            'ts':    time.time()
        }).encode()

        # send to all connected devices
        dead = []
        for client in self.clients:
            try:
                # send length prefix then data
                length = len(msg).to_bytes(4, 'big')
                client.send(length + msg)
                print(f"[BlinkUI] ✓ Pushed reload to device")
            except:
                dead.append(client)

        for c in dead:
            self.clients.remove(c)

    def _get_python_files(self):
        files = []
        for pattern in ['screens/*.py', 'components/*.py', 'main.py']:
            files.extend(str(p) for p in self.project_dir.glob(pattern))
        return files

    def _hash(self, path):
        try:
            return hashlib.md5(Path(path).read_bytes()).hexdigest()
        except:
            return ''


def start_server(project_dir='.'):
    server = HotReloadServer(project_dir)
    server.start()


if __name__ == '__main__':
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else '.'
    start_server(project)
