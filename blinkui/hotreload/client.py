"""
BlinkUI Hot Reload Client
Runs on the Android device, receives updates from the server.
"""

import socket
import json
import threading
import time


class HotReloadClient:
    PORT = 8974

    def __init__(self, server_ip: str, on_reload):
        self.server_ip = server_ip
        self.on_reload = on_reload
        self.sock      = None
        self.running   = False

    def connect(self):
        self.running = True
        thread = threading.Thread(target=self._connect_loop, daemon=True)
        thread.start()

    def _connect_loop(self):
        while self.running:
            try:
                print(f"[HotReload] Connecting to {self.server_ip}:{self.PORT}...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_ip, self.PORT))
                print(f"[HotReload] Connected to dev server")
                self._listen()
            except Exception as e:
                print(f"[HotReload] Connection failed: {e}")
                time.sleep(2)

    def _listen(self):
        try:
            while self.running:
                # read 4-byte length prefix
                raw_len = self._recv_exact(4)
                if not raw_len:
                    break
                length = int.from_bytes(raw_len, 'big')

                # read message
                raw_msg = self._recv_exact(length)
                if not raw_msg:
                    break

                msg = json.loads(raw_msg.decode())
                if msg['type'] == 'reload':
                    print(f"[HotReload] Reload received")
                    self.on_reload(msg['files'])
        except Exception as e:
            print(f"[HotReload] Connection lost: {e}")

    def _recv_exact(self, n):
        data = b''
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def disconnect(self):
        self.running = False
        if self.sock:
            self.sock.close()
