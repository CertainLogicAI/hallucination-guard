#!/usr/bin/env python3
"""Product health check — validates all products under products/."""

import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_DIR = os.path.join(BASE_DIR, "products")
LOGS_DIR = os.path.join(BASE_DIR, "logs")


def log(message, level="info"):
    prefix = {"info": "[INFO]", "warn": "[WARN]", "error": "[ERROR]", "ok": "[OK]"}.get(level, "[INFO]")
    print(f"{prefix} {message}")


def check_json(path, required_keys=None):
    """Return (ok: bool, data: dict|None, errors: list)"""
    errors = []
    if not os.path.exists(path):
        return False, None, [f"missing: {path}"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, None, [f"invalid JSON: {path} — {e}"]
    except Exception as e:
        return False, None, [f"read error: {path} — {e}"]

    if required_keys:
        missing = [k for k in required_keys if k not in data]
        if missing:
            errors.append(f"missing keys in {os.path.basename(path)}: {missing}")
    return len(errors) == 0, data, errors


def count_facts(data):
    """Count facts in coding_facts.json (nested under 'facts' key)."""
    if isinstance(data, dict) and "facts" in data and isinstance(data["facts"], dict):
        return len(data["facts"])
    if isinstance(data, (list, dict)):
        return len(data)
    return 0


def count_queries(data):
    """Count total individual queries in coding_queries.json (nested under 'mappings' key)."""
    if isinstance(data, dict) and "mappings" in data and isinstance(data["mappings"], list):
        return sum(len(m.get("queries", [])) for m in data["mappings"])
    if isinstance(data, (list, dict)):
        return len(data)
    return 0


def check_coding_agent(product_dir):
    """Health checks for the coding_agent_pro product."""
    results = {"product": "coding_agent", "pass": True, "checks": []}

    # 1. inventory.json
    inv_path = os.path.join(product_dir, "inventory.json")
    ok, inv, errs = check_json(inv_path, required_keys=["product", "version", "status"])
    for e in errs:
        results["checks"].append({"file": "inventory.json", "status": "fail", "detail": e})
        results["pass"] = False
    if ok:
        results["checks"].append({
            "file": "inventory.json",
            "status": "pass",
            "detail": f"product={inv.get('product')}, version={inv.get('version')}, status={inv.get('status')}"
        })
        facts_expected = inv.get("facts", {}).get("total")
        queries_expected = inv.get("queries", {}).get("total_mappings")
    else:
        facts_expected = queries_expected = None

    # 2. coding_facts.json
    facts_path = os.path.join(product_dir, "coding_facts.json")
    ok, facts_data, errs = check_json(facts_path)
    for e in errs:
        results["checks"].append({"file": "coding_facts.json", "status": "fail", "detail": e})
        results["pass"] = False
    if ok:
        facts_count = count_facts(facts_data)
        status = "pass"
        detail = f"{facts_count} facts"
        if facts_expected is not None and facts_count != facts_expected:
            status = "fail"
            detail += f" (expected {facts_expected})"
            results["pass"] = False
        results["checks"].append({"file": "coding_facts.json", "status": status, "detail": detail})

    # 3. coding_queries.json
    queries_path = os.path.join(product_dir, "coding_queries.json")
    ok, queries_data, errs = check_json(queries_path)
    for e in errs:
        results["checks"].append({"file": "coding_queries.json", "status": "fail", "detail": e})
        results["pass"] = False
    if ok:
        queries_count = count_queries(queries_data)
        status = "pass"
        detail = f"{queries_count} queries"
        if queries_expected is not None and queries_count != queries_expected:
            status = "fail"
            detail += f" (expected {queries_expected})"
            results["pass"] = False
        results["checks"].append({"file": "coding_queries.json", "status": status, "detail": detail})

    return results


def discover_products():
    if not os.path.isdir(PRODUCTS_DIR):
        return []
    return [d for d in os.listdir(PRODUCTS_DIR) if os.path.isdir(os.path.join(PRODUCTS_DIR, d))]


def main():
    now = datetime.now(timezone.utc).isoformat()
    overall_pass = True
    product_results = []

    products = discover_products()
    if not products:
        log("No products found under products/", level="warn")
    else:
        log(f"Discovered {len(products)} product(s): {', '.join(products)}")

    for prod in products:
        prod_dir = os.path.join(PRODUCTS_DIR, prod)
        if prod == "coding_agent":
            res = check_coding_agent(prod_dir)
        else:
            res = {"product": prod, "pass": True, "checks": []}
            for fname in ["inventory.json"]:
                fpath = os.path.join(prod_dir, fname)
                ok, _, errs = check_json(fpath)
                for e in errs:
                    res["checks"].append({"file": fname, "status": "fail", "detail": e})
                    res["pass"] = False
                if ok:
                    res["checks"].append({"file": fname, "status": "pass", "detail": "valid JSON"})
        product_results.append(res)
        if not res["pass"]:
            overall_pass = False

    # Print human-readable summary
    print(f"\n=== Product Health Check ===")
    print(f"Timestamp: {now}")
    print(f"Products checked: {len(products)}")
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    print()

    for res in product_results:
        status_icon = "✓" if res["pass"] else "✗"
        print(f"{status_icon} {res['product']}")
        for c in res["checks"]:
            icon = "  ✓" if c["status"] == "pass" else "  ✗"
            print(f"    {icon} {c['file']}: {c['detail']}")
        print()

    # Write JSON report
    report = {
        "timestamp": now,
        "overall_pass": overall_pass,
        "products_checked": len(products),
        "results": product_results,
    }
    os.makedirs(LOGS_DIR, exist_ok=True)
    json_path = os.path.join(LOGS_DIR, "product_health_latest.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    log(f"JSON report written to: {json_path}")

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
