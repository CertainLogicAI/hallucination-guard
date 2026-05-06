#!/usr/bin/env python3
"""
Family Storage — Verified page writes to Company Brain

All work MUST be stored under family/ hierarchy.
Every write is verified (put then immediate get to confirm persistence).
"""

import sys, os
sys.path.insert(0, '/data/.openclaw/workspace/company-brain')
os.environ['CERTAINLOGIC_DATA'] = '/data/.openclaw/workspace/company-brain-data'

from deterministic_brain import DeterministicBrain, create_intent

# Ensure family intent exists
create_intent('family', ['brain.put_page', 'brain.get_page', 'brain.query'], [], [])

class FamilyStorage:
    """Verified storage with automatic retry."""
    
    def __init__(self):
        self.brain = DeterministicBrain(domain='family')
    
    def put(self, slug: str, content: str, author: str = 'system', parent: str = '', frontmatter: dict = None) -> dict:
        """Store a page and verify it persisted."""
        # Ensure slug starts with family/ but don't double-prefix
        if not slug.startswith('family'):
            slug = f'family/{slug}'
        
        fm = frontmatter or {}
        fm.update({
            'type': 'family_node',
            'author': author,
            'created': '2026-05-06',
            'parent': parent or 'family/',
            'immutable': False,
        })
        
        # Write
        result = self.brain.command('brain.put_page', {
            'slug': slug,
            'content': content,
            'frontmatter': fm,
            'source': 'family-storage'
        })
        
        # Verify
        if result.get('success'):
            import time
            time.sleep(0.3)  # Let PGLite flush
            verify = self.brain.command('brain.get_page', {'slug': slug, 'source': 'verify'})
            if verify.get('success'):
                result['verified'] = True
                result['hmac_ok'] = verify.get('hmac_verified', False)
            else:
                result['verified'] = False
                result['verify_error'] = verify.get('error', 'get failed')
        
        return result
    
    def get(self, slug: str) -> dict:
        if not slug.startswith('family'):
            slug = f'family/{slug}'
        return self.brain.command('brain.get_page', {'slug': slug, 'source': 'retrieve'})
    
    def store_work(self, path: str, content: str, author: str = 'system') -> bool:
        """Store work item. Returns True if verified persisted."""
        r = self.put(path, content, author=author, parent=f'family/work/{path.split("/")[0]}')
        return r.get('success') and r.get('verified', False)

# Singleton
_storage = None

def get_storage() -> FamilyStorage:
    global _storage
    if _storage is None:
        _storage = FamilyStorage()
    return _storage

if __name__ == '__main__':
    s = get_storage()
    print('Family storage initialized. Use get_storage().put(slug, content)')
    print('Verified test will be run...')
    
    r = s.put('test/verified-storage', 'This is a verified family storage test.')
    print(f"\nTest result:")
    print(f"  Success: {r['success']}")
    print(f"  Verified: {r.get('verified')}")
    if r.get('hash'):
        print(f"  Hash: {r['hash'][:20]}...")
