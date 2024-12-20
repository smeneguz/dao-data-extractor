# src/utils/cache.py
import json
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class Cache:
    """Simple file-based cache implementation"""
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_metadata()

    def _load_metadata(self):
        """Load or initialize cache metadata"""
        self.metadata_path = self.cache_dir / 'metadata.json'
        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.metadata = {'last_updated': {}, 'versions': {}}
            self._save_metadata()

    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from cache"""
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Corrupted cache file: {key}")
            return None

    def set(self, key: str, data: Dict[str, Any], version: str = '1'):
        """Store data in cache with versioning"""
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.metadata['last_updated'][key] = int(time.time())
            self.metadata['versions'][key] = version
            self._save_metadata()
            
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")

    def is_valid(self, key: str, max_age: int = 86400) -> bool:
        """Check if cached data is valid"""
        last_updated = self.metadata['last_updated'].get(key)
        if not last_updated:
            return False
            
        age = int(time.time()) - last_updated
        return age < max_age