import json
import hashlib
import os
from typing import Dict, Any, Optional

class CacheManager:
    """
    Manages incremental file modification checks and preserves 
    previously computed schemas to allow error recovery during parser failures.
    """
    def __init__(self, cache_filepath: str = ".repo-anchor.cache.json"):
        self.cache_filepath = cache_filepath
        self.cache_data: Dict[str, Dict[str, str]] = {}
        self.load_cache()

    def load_cache(self) -> None:
        if os.path.exists(self.cache_filepath):
            try:
                with open(self.cache_filepath, "r", encoding="utf-8") as f:
                    self.cache_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.cache_data = {}
        else:
            self.cache_data = {}

    def save_cache(self) -> None:
        try:
            with open(self.cache_filepath, "w", encoding="utf-8") as f:
                json.dump(self.cache_data, f, indent=4)
        except OSError:
            pass

    @staticmethod
    def calculate_hash(filepath: str) -> Optional[str]:
        if not os.path.exists(filepath):
            return None
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except OSError:
            return None

    def is_changed(self, filepath: str) -> bool:
        current_hash = self.calculate_hash(filepath)
        if current_hash is None:
            return True
        cached_entry = self.cache_data.get(filepath)
        if not cached_entry:
            return True
        return current_hash != cached_entry.get("hash")

    def get_cached_skeleton(self, filepath: str) -> Optional[str]:
        entry = self.cache_data.get(filepath)
        if entry:
            return entry.get("skeleton")
        return None

    def update_cache(self, filepath: str, skeleton: str) -> None:
        current_hash = self.calculate_hash(filepath)
        if current_hash:
            self.cache_data[filepath] = {
                "hash": current_hash,
                "skeleton": skeleton
            }