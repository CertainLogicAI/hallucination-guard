#!/usr/bin/env python3
"""
CLI for CertainLogic Verifier.

Zero-friction install and run:
    hallucination-guard install                    # Free tier — 100 facts
    hallucination-guard install --paid --key XXXX  # Full pack — 333 facts
    hallucination-guard serve                      # Start API server
    hallucination-guard status                     # Check install status
    hallucination-guard verify "query" "response"  # Quick validation
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="hallucination-guard",
        description="CertainLogic Verifier — deterministic AI verification, self-hosted",
    )
    sub = parser.add_subparsers(dest="command", help="Commands")

    # install
    install_p = sub.add_parser("install", help="Install fact pack (free or paid)")
    install_p.add_argument("--paid", action="store_true", help="Install paid tier (requires --key)")
    install_p.add_argument("--key", help="License key for paid tier")
    install_p.add_argument("--data-dir", help="Custom data directory")

    # serve
    serve_p = sub.add_parser("serve", help="Start API server")
    serve_p.add_argument("--host", default="0.0.0.0", help="Bind address")
    serve_p.add_argument("--port", type=int, default=8000, help="Port")

    # status
    status_p = sub.add_parser("status", help="Show installation status")
    status_p.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    status_p.add_argument("--data-dir", help="Custom data directory")

    # update
    update_p = sub.add_parser("update", help="Update paid pack to latest")
    update_p.add_argument("--data-dir", help="Custom data directory")

    # verify
    verify_p = sub.add_parser("verify", help="Quick one-off validation")
    verify_p.add_argument("query", help="Query to validate")
    verify_p.add_argument("response", help="AI response to check")

    # report
    report_p = sub.add_parser("report", help="Show domain gate hit rate report")
    report_p.add_argument("--data-dir", help="Custom data directory")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "install":
        _cmd_install(args)
    elif args.command == "serve":
        _cmd_serve(args)
    elif args.command == "status":
        _cmd_status(args)
    elif args.command == "update":
        _cmd_update(args)
    elif args.command == "verify":
        _cmd_verify(args)
    elif args.command == "report":
        _cmd_report(args)


def _cmd_install(args):
    from pathlib import Path
    from hallucination_guard.packs import install_pack

    data_dir = Path(args.data_dir) if args.data_dir else None
    tier = "paid" if args.paid else "free"
    key = args.key if args.paid else None

    result = install_pack(
        pack_name="coder",
        license_key=key,
        data_dir=data_dir,
    )

    if result.get("status") != "ok":
        print(f"❌ {result.get('message', 'Installation failed')}")
        sys.exit(1)

    print(result["message"])


def _cmd_serve(args):
    import uvicorn
    from pathlib import Path
    from hallucination_guard.packs import get_data_dir

    data_dir = get_data_dir()
    env_file = data_dir / ".env"

    print(f"🚀 Starting CertainLogic Verifier on {args.host}:{args.port}")
    if env_file.exists():
        print(f"   Data directory: {data_dir}")
        with open(env_file) as f:
            for line in f:
                if line.strip():
                    print(f"   {line.strip()}")

    uvicorn.run(
        "hallucination_guard.__main__:app",
        host=args.host,
        port=args.port,
    )


def _cmd_status(args):
    from pathlib import Path
    from hallucination_guard.packs import pack_status

    data_dir = Path(args.data_dir) if args.data_dir else None
    result = pack_status(data_dir=data_dir)

    if args.as_json:
        print(json.dumps(result, indent=2, default=str))
        return

    if not result.get("installed"):
        print("📦 Not installed. Run: hallucination-guard install")
        return

    tier_icon = "💎" if result.get("tier") == "paid" else "🆓"
    print(f"📦 Coder Pack {tier_icon}")
    print(f"   Tier:     {result.get('tier', 'unknown')}")
    print(f"   Facts:    {result.get('facts_count', 0)}")
    print(f"   Cache:    {result.get('cache_entries', 0)} entries")
    print(f"   Warmed:   {'✅ Yes' if result.get('cache_warmed') else '❌ No'}")
    if result.get("installed_at"):
        print(f"   Installed: {result['installed_at'][:19]}")
    if result.get("updated_at"):
        print(f"   Updated:  {result['updated_at'][:19]}")


def _cmd_update(args):
    from pathlib import Path
    from hallucination_guard.packs import update_pack

    data_dir = Path(args.data_dir) if args.data_dir else None
    result = update_pack(data_dir=data_dir)

    if result.get("status") != "ok":
        print(f"❌ {result.get('message', 'Update failed')}")
        sys.exit(1)

    print(f"✅ {result.get('message', 'Updated')}")


def _cmd_report(args):
    from pathlib import Path
    from hallucination_guard.domain_gate import HitRateTracker

    data_dir = Path(args.data_dir) if args.data_dir else None
    tracker = HitRateTracker(data_dir=data_dir)
    tracker.print_report()


def _cmd_verify(args):
    from hallucination_guard.packs import get_active_facts_path
    from hallucination_guard.hallucination_detector import HallucinationDetector

    detector = HallucinationDetector(facts_db_path=str(get_active_facts_path()))
    result = detector.validate(args.query, args.response)

    icon = "✅" if result.get("valid") else "❌"
    print(f"{icon} Valid: {result.get('valid')}")
    print(f"   Confidence: {result.get('confidence', '?')}")
    if result.get("flags"):
        for flag in result["flags"]:
            print(f"   ⚠️  {flag}")


if __name__ == "__main__":
    main()
