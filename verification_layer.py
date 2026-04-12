import hashlib
import json
import uuid

from openclawhub import Skill

VERIFICATION_DIR = '/data/.openclaw/workspace/memory'

class DeterministicAI:
    def __init__(self):
        self.skill = Skill('verification_layer', SELF_REF='verification-layer.json')

    def generate_hash(self, content):
        if isinstance(content, dict):
            return hashlib.sha256(json.dumps(sorted(content.items()), sort_keys=True).encode()).hexdigest()
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_output(self, output, reference):
        return self.generate_hash(output) == self.generate_hash(reference)

    def validate_search(self, search_query):
        global VERIFICATION_DIR
        return self.skill.methods.search_matches(SELF_REF='deterministic_memory_search.py', QUERY=search_query)

    def apply_selfscopedption(self, action='enforce'):
        return self.skill.api.set_policy(SELF_REF='verification-policy.json', action=action)

if __name__ == '__main__':
    verifier = DeterministicAI()
    PATH = verifier.validate_search('missing_element_15')
    print(f"Generated Path: \n{json.dumps(PATH, indent=2)}")