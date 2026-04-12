#!/usr/bin/env python3
"""
Cache Manager - Automatic cleanup for workspace-cache.json
Handles eviction of old/unused entries while maintaining integrity hashes.
"""

import os
import json
import time
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

CACHE_FILE = "/data/.openclaw/workspace/workspace-cache.json"
CACHE_LIMIT_MB = 50
ENTRY_MAX_AGE_DAYS = 30
MIN_USAGE_COUNT = 2
BACKUP_DIR = "/data/.openclaw/workspace/backups/cache"

class CacheManager:
    def __init__(self):
        self.cache = self.load_cache()
        Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    
    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        return {
            "_metadata": {"version": "2.1", "created": int(time.time())},
            "files": [],
            "index": {},
            "generated": int(time.time())
        }
    
    def save_cache(self):
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
        # Update integrity hash after save
        self.update_cache_hash()
    
    def update_cache_hash(self):
        """Update SHA-256 hash of the entire cache file"""
        with open(CACHE_FILE, 'rb') as f:
            cache_hash = hashlib.sha256(f.read()).hexdigest()
        self.cache["_metadata"]["cache_hash"] = cache_hash
        self.cache["_metadata"]["last_modified"] = int(time.time())
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def cache_size_mb(self):
        return os.path.getsize(CACHE_FILE) / 1024 / 1024
    
    def should_evict(self):
        threshold = CACHE_LIMIT_MB * 0.8  # 80% of limit
        return self.cache_size_mb() > threshold
    
    def get_entries_by_age(self):
        """Group entries by age for tiered eviction"""
        now = time.time()
        old_entries = []
        recent_entries = []
        
        files = self.cache.get("files", [])
        for i, entry in enumerate(files):
            age_days = (now - entry.get("timestamp", now)) / 86400
            if age_days > ENTRY_MAX_AGE_DAYS:
                old_entries.append((i, entry, age_days))
            else:
                recent_entries.append((i, entry, age_days))
        
        return old_entries, recent_entries
    
    def evict_entries(self, indices_to_remove):
        """Remove entries by index (reverse order to maintain indices)"""
        if not indices_to_remove:
            return 0
        
        indices = set(indices_to_remove)
        original_count = len(self.cache.get("files", []))
        
        # Remove from files array
        self.cache["files"] = [
            entry for i, entry in enumerate(self.cache["files"])
            if i not in indices
        ]
        
        removed = original_count - len(self.cache["files"])
        print(f"  Removed {removed} entries")
        return removed
    
    def create_backup(self):
        """Create timestamped backup of current cache"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"cache-{timestamp}.json")
        shutil.copy2(CACHE_FILE, backup_path)
        
        # Also keep a symlink to latest backup
        latest_link = os.path.join(BACKUP_DIR, "latest-cache.json")
        if os.path.exists(latest_link) or os.path.islink(latest_link):
            os.remove(latest_link)
        os.symlink(backup_path, latest_link)
        
        return backup_path
    
    def run_cleanup(self):
        """Main cleanup routine"""
        print("=" * 60)
        print("CACHE CLEANUP - Starting")
        print("=" * 60)
        
        initial_size = self.cache_size_mb()
        print(f"Current cache size: {initial_size:.1f} MB")
        print(f"Current file count: {len(self.cache.get('files', []))}")
        print(f"Limit threshold: {CACHE_LIMIT_MB * 0.8:.1f} MB (80% of {CACHE_LIMIT_MB} MB)")
        print()
        
        # 1. Always create backup before cleanup
        backup_path = self.create_backup()
        print(f"✓ Backup created: {backup_path}")
        
        # 2. Check if eviction needed
        if not self.should_evict():
            print("✓ Cache size OK - no eviction needed")
            self.cache["_metadata"]["last_cleanup"] = int(time.time())
            self.cache["_metadata"]["last_cleanup_reason"] = "no_action_needed"
            self.save_cache()
            return
        
        print("⚠ Cache exceeds threshold - starting eviction...")
        print()
        
        # 3. Identify old entries (>30 days) - FIRST PRIORITY for removal
        old_entries, recent_entries = self.get_entries_by_age()
        print(f"Found {len(old_entries)} old entries (>{ENTRY_MAX_AGE_DAYS} days)")
        print(f"Found {len(recent_entries)} recent entries (<={ENTRY_MAX_AGE_DAYS} days)")
        
        # 4. Evict old entries first
        if old_entries:
            print("\n--- Phase 1: Removing old entries ---")
            old_indices = [i for i, _, _ in old_entries]
            self.evict_entries(old_indices)
        
        # 5. Check if we're still over threshold
        current_size = self.cache_size_mb()
        if not self.should_evict():
            print(f"\n✓ Cache size OK after phase 1: {current_size:.1f} MB")
            self.cache["_metadata"]["last_cleanup"] = int(time.time())
            self.cache["_metadata"]["last_cleanup_reason"] = "old_entries_removed"
            self.save_cache()
            return
        
        # 6. If still over, remove least-used recent entries
        print(f"\n⚠ Still over threshold ({current_size:.1f} MB) - removing unused entries...")
        
        # Sort by age (oldest first among recent)
        sorted_recent = sorted(recent_entries, key=lambda x: x[2], reverse=True)
        
        entries_to_remove = []
        target_size = CACHE_LIMIT_MB * 0.6  # Aim for 60% after cleanup
        
        for idx, entry, age in sorted_recent:
            if self.cache_size_mb() <= target_size:
                break
            entries_to_remove.append(idx)
        
        if entries_to_remove:
            print(f"\n--- Phase 2: Removing {len(entries_to_remove)} unused recent entries ---")
            self.evict_entries(entries_to_remove)
        
        # 7. Update metadata
        final_size = self.cache_size_mb()
        self.cache["_metadata"]["last_cleanup"] = int(time.time())
        self.cache["_metadata"]["last_cleanup_reason"] = "aggressive_cleanup"
        self.cache["_metadata"]["entries_removed"] = len(old_entries) + len(entries_to_remove)
        self.cache["_metadata"]["size_before_mb"] = round(initial_size, 2)
        self.cache["_metadata"]["size_after_mb"] = round(final_size, 2)
        self.save_cache()
        
        print("\n" + "=" * 60)
        print("CLEANUP COMPLETE")
        print(f"  Before: {initial_size:.1f} MB")
        print(f"  After:  {final_size:.1f} MB")
        print(f"  Saved:  {initial_size - final_size:.1f} MB")
        print(f"  Files:  {len(self.cache.get('files', []))}")
        print("=" * 60)
    
    def get_status(self):
        """Return cache status for monitoring"""
        current_size = self.cache_size_mb()
        entries = len(self.cache.get("files", []))
        metadata = self.cache.get("_metadata", {})
        
        status = "healthy"
        if not self.should_evict():
            status = "healthy"
        elif current_size > CACHE_LIMIT_MB:
            status = "critical"
        else:
            status = "warning"
        
        return {
            "status": status,
            "size_mb": round(current_size, 2),
            "entries": entries,
            "limit_mb": CACHE_LIMIT_MB,
            "usage_percent": round((current_size / CACHE_LIMIT_MB) * 100, 1),
            "last_cleanup": datetime.fromtimestamp(
                metadata.get("last_cleanup", 0)
            ).strftime("%Y-%m-%d %H:%M:%S") if metadata.get("last_cleanup") else "never",
            "cache_hash": metadata.get("cache_hash", "not_set"),
            "version": metadata.get("version", "unknown")
        }
    
    def verify_integrity(self):
        """Verify cache hash matches current file"""
        metadata = self.cache.get("_metadata", {})
        stored_hash = metadata.get("cache_hash")
        
        if not stored_hash:
            # No hash set yet - generate one
            self.update_cache_hash()
            return True, "Hash generated"
        
        # Recalculate hash
        self.update_cache_hash()
        new_hash = self.cache["_metadata"]["cache_hash"]
        
        if stored_hash == new_hash:
            return True, "Cache integrity verified"
        else:
            return False, f"Hash mismatch! Expected: {stored_hash[:16]}... Got: {new_hash[:16]}..."

def main():
    import sys
    
    manager = CacheManager()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "cleanup":
            manager.run_cleanup()
        elif cmd == "status":
            status = manager.get_status()
            print(json.dumps(status, indent=2))
        elif cmd == "verify":
            valid, message = manager.verify_integrity()
            print(f"{'✓' if valid else '✗'} {message}")
        elif cmd == "hash":
            manager.update_cache_hash()
            print(f"Cache hash: {manager.cache['_metadata']['cache_hash']}")
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: cache_manager.py [cleanup|status|verify|hash]")
    else:
        # Default: run cleanup
        manager.run_cleanup()
        status = manager.get_status()
        print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
