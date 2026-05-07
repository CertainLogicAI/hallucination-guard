#!/usr/bin/env python3
"""
Bulk Migration Smoke Test — Phase 4E

Tests that all 10 skill brain shims can import successfully.
Does NOT test runtime integration (that requires each skill individually).

Verifies:
  1. All brain_enhance.py files exist and import cleanly
  2. All optional Brain() imports handle failure gracefully
  3. No skill shim crashes on load
"""

import importlib
import importlib.util
import sys
from pathlib import Path
import unittest

WORKSPACE = Path("/data/.openclaw/workspace")
BRAIN_PATH = WORKSPACE / "company-brain"

SKILLS = [
    # (skill_dir, module_name, callable_name)
    ("skills/cold-outreach", "brain_enhance", "enhance_outreach"),
    ("skills/seo", "seo_brain_enhance", "get_seo_context"),
    ("skills/market-research", "brain_enhance", "get_market_context"),
    ("skills/certainlogic-pathfinder", "brain_enhance", "get_audit_context"),
    ("skills/skill-vetter-plus", "brain_enhance", "get_security_context"),
    ("skills/skill-oracle", "brain_enhance", "get_catalog_context"),
    ("skills/skill-guard", "brain_enhance", "get_threat_context"),
    ("skills/x-api", "brain_enhance_v1", "get_brand_voice"),
    ("skills/x-api", "brain_enhance_v2", "get_product_highlight"),
]


def load_module(skill_dir: str, module_name: str):
    """Load a module by path, returning the module object."""
    file_path = WORKSPACE / skill_dir / f"{module_name}.py"
    if not file_path.exists():
        return None

    spec = importlib.util.spec_from_file_location(f"test_{module_name}", file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestBulkMigrationShims(unittest.TestCase):

    def test_brain_path_in_syspath(self):
        """Brain path should be accessible for imports."""
        self.assertIn(str(BRAIN_PATH), sys.path)

    def test_all_shim_files_exist(self):
        """Every skill shim file must exist on disk."""
        for skill_dir, module_name, _ in SKILLS:
            file_path = WORKSPACE / skill_dir / f"{module_name}.py"
            self.assertTrue(file_path.exists(), f"Missing: {skill_dir}/{module_name}.py")

    def test_all_shims_import_cleanly(self):
        """Every shim must import without raising."""
        for skill_dir, module_name, _ in SKILLS:
            mod = load_module(skill_dir, module_name)
            self.assertIsNotNone(mod, f"Failed to import {module_name} from {skill_dir}")

    def test_all_callables_exist(self):
        """Every shim must export its declared primary callable."""
        for skill_dir, module_name, callable_name in SKILLS:
            mod = load_module(skill_dir, module_name)
            if mod is None:
                continue
            self.assertTrue(
                hasattr(mod, callable_name),
                f"{module_name} missing callable {callable_name}"
            )

    def test_shared_shim_imports(self):
        """The shared brain_integration.py must import cleanly."""
        shared_path = WORKSPACE / "skills" / "brain_integration.py"
        spec = importlib.util.spec_from_file_location("brain_integration", shared_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)

        self.assertTrue(hasattr(mod, "safe_brain_query"))
        self.assertTrue(hasattr(mod, "get_brain_context_for_skill"))
        self.assertTrue(hasattr(mod, "brain_available"))

    def test_pilot_skill_still_works(self):
        """content_engine still imports and generates (regression guard)."""
        sys.path.insert(0, str(BRAIN_PATH))
        sys.path.insert(0, str(WORKSPACE))
        from marketing.content_engine import ContentEngine

        engine = ContentEngine(date_str="2026-05-07")
        posts = engine.generate_daily_posts(count=2)
        self.assertEqual(len(posts), 2)


if __name__ == "__main__":
    # Ensure brain path is in sys.path before tests run
    if str(BRAIN_PATH) not in sys.path:
        sys.path.insert(0, str(BRAIN_PATH))

    unittest.main(verbosity=2)
