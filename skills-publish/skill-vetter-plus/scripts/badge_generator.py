#!/usr/bin/env python3
"""
Skill Vetter Plus — Badge Generator
Creates "CertainLogic Certified" badges for passing skills.
"""
import hashlib, json
from datetime import datetime
from pathlib import Path

CERT_REGISTRY = Path("/data/.openclaw/workspace/skills-publish/skill-vetter-plus/registry.json")

def generate_badge(skill_id: str, cert_id: str, version: str = "1.0") -> str:
    """Generate markdown badge for certified skill."""
    badge = f"""[![CertainLogic Certified](https://img.shields.io/badge/CertainLogic-Certified%20v{cert_id[:8]}-blue)](https://certainlogic.ai/certified/{cert_id})
**Certified:** {datetime.now().strftime("%Y-%m-%d")} | **ID:** `{cert_id}`
"""
    return badge

def save_certification(skill_id: str, cert_id: str, report: dict):
    """Save certification to registry."""
    registry = {}
    if CERT_REGISTRY.exists():
        registry = json.load(open(CERT_REGISTRY))
    
    registry[cert_id] = {
        "skill_id": skill_id,
        "certified_at": datetime.now().isoformat(),
        "checks": {c["name"]: c["passed"] for c in report.get("checks", [])},
        "status": "active"
    }
    
    CERT_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    json.dump(registry, open(CERT_REGISTRY, "w"), indent=2)

def verify_cert(cert_id: str) -> dict:
    """Verify a certification ID is valid."""
    if not CERT_REGISTRY.exists():
        return {"valid": False, "error": "Registry not found"}
    
    registry = json.load(open(CERT_REGISTRY))
    if cert_id in registry:
        return {"valid": True, **registry[cert_id]}
    return {"valid": False, "error": "Certification not found"}
