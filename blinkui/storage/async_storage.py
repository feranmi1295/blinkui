# ─────────────────────────────────────────
# BlinkUI Async Storage
# Persistent key-value storage for mobile apps
# Survives app restarts
# ─────────────────────────────────────────

import asyncio
import json
import os
import threading
from pathlib import Path


# ─────────────────────────────────────────
# Storage location
# On mobile this maps to the app's
# private documents directory
# On Linux it maps to ~/.blinkui/storage
# ─────────────────────────────────────────
def _get_storage_dir() -> Path:
    home = Path.home()
    storage_dir = home / ".blinkui" / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


class AsyncStorage:
    """
    Persistent async key-value storage.

    All operations are async so they never
    block the UI thread.

    Usage:
        from blinkui.storage import storage

        # save a value
        await storage.set("theme", "dark")

        # get a value
        theme = await storage.get("theme")

        # get with fallback
        theme = await storage.get("theme", default="light")

        # delete
        await storage.delete("theme")

        # check if key exists
        exists = await storage.has("auth_token")

        # save a dict or list — serialized as JSON automatically
        await storage.set("user", {"id": 1, "name": "John"})
        user = await storage.get("user")
        print(user["name"])  # John

        # get all keys
        keys = await storage.keys()

        # clear everything
        await storage.clear()
    """

    def __init__(self):
        self._dir   = _get_storage_dir()
        self._lock  = threading.Lock()
        self._cache = {}         # in-memory cache for fast reads
        self._load_cache()

    def _load_cache(self):
        """Load all stored values into memory on startup."""
        try:
            index_path = self._dir / "index.json"
            if index_path.exists():
                with open(index_path, "r") as f:
                    self._cache = json.load(f)
        except Exception:
            self._cache = {}

    def _save_cache(self):
        """Persist cache to disk."""
        try:
            index_path = self._dir / "index.json"
            with open(index_path, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            print(f"[Storage] Failed to save: {e}")

    def _sync_set(self, key: str, value) -> bool:
        with self._lock:
            self._cache[key] = value
            self._save_cache()
            return True

    def _sync_get(self, key: str, default=None):
        with self._lock:
            return self._cache.get(key, default)

    def _sync_delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._save_cache()
                return True
            return False

    def _sync_has(self, key: str) -> bool:
        with self._lock:
            return key in self._cache

    def _sync_keys(self) -> list:
        with self._lock:
            return list(self._cache.keys())

    def _sync_clear(self) -> bool:
        with self._lock:
            self._cache.clear()
            self._save_cache()
            return True

    def _sync_get_all(self) -> dict:
        with self._lock:
            return dict(self._cache)

    # ─────────────────────────────────────
    # Public async API
    # ─────────────────────────────────────

    async def set(self, key: str, value) -> bool:
        """
        Save a value. Supports strings, numbers,
        booleans, dicts, and lists.

        Usage:
            await storage.set("count", 42)
            await storage.set("user", {"name": "John"})
            await storage.set("token", "abc123")
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self._sync_set(key, value)
        )
        print(f"[Storage] Set: {key}")
        return result

    async def get(self, key: str, default=None):
        """
        Get a value by key.
        Returns default if key does not exist.

        Usage:
            token = await storage.get("token")
            count = await storage.get("count", default=0)
        """
        loop = asyncio.get_event_loop()
        value = await loop.run_in_executor(
            None, lambda: self._sync_get(key, default)
        )
        return value

    async def delete(self, key: str) -> bool:
        """
        Delete a value by key.
        Returns True if deleted, False if key not found.

        Usage:
            await storage.delete("token")
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self._sync_delete(key)
        )
        if result:
            print(f"[Storage] Deleted: {key}")
        else:
            print(f"[Storage] Key not found: {key}")
        return result

    async def has(self, key: str) -> bool:
        """
        Check if a key exists.

        Usage:
            if await storage.has("token"):
                self.navigate("dashboard")
            else:
                self.navigate("login")
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self._sync_has(key)
        )

    async def keys(self) -> list:
        """
        Get all stored keys.

        Usage:
            all_keys = await storage.keys()
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._sync_keys
        )

    async def get_all(self) -> dict:
        """
        Get everything in storage as a dict.

        Usage:
            everything = await storage.get_all()
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._sync_get_all
        )

    async def clear(self) -> bool:
        """
        Delete everything in storage.

        Usage:
            await storage.clear()  # logout, reset app
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._sync_clear
        )
        print("[Storage] Cleared all data")
        return result

    async def set_many(self, data: dict) -> bool:
        """
        Save multiple values at once.

        Usage:
            await storage.set_many({
                "token":    "abc123",
                "user_id":  42,
                "theme":    "dark"
            })
        """
        for key, value in data.items():
            await self.set(key, value)
        return True

    async def get_many(self, keys: list) -> dict:
        """
        Get multiple values at once.

        Usage:
            result = await storage.get_many(["token", "user_id", "theme"])
        """
        result = {}
        for key in keys:
            result[key] = await self.get(key)
        return result


# ─────────────────────────────────────────
# Global storage instance
# Import and use anywhere in your app
# ─────────────────────────────────────────
storage = AsyncStorage()