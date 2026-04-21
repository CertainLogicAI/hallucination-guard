#!/usr/bin/env python3
"""
CLI for CertainLogic Verifier.

Usage:
    hallucination-guard serve              Start the API server
    hallucination-guard install-pack       Install a fact pack (free or paid)
    hallucination-guard update-pack        Update installed pack (paid subscription)
    hallucination-guard status             Show pack and system status
    hallucination-guard verify <query>     Quick one-off validation from CLI
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="hallucination-guard",
        description="CertainLogic Verifier — deterministic AI verification middleware",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # serve
    serve_p = sub.add_parser("serve", help="Start the API server")
    serve_p.add_argument("--host", default="0.0.0.0", help="Bind address")
    serve_p.add_argument("--port", type=int, default=8000, help="Port")

    # install-pack
    install_p = sub.add_parser("install-pack", help="Install a fact pack")
    install_p.add_argument("pack", nargs="?", default="coder", help="Pack name (default: coder)")
    install_p.add_argument("--key", help="License key for paid pack")
    install_p.add_argument("--data-dir", help="Custom data directory")

    # update-pack
    update_p = sub.add_parser("update-pack", help="Update installed pack")
    update_p.add_argument("pack", nargs="?", default="coder", help="Pack name")
    update_p.add_argument("--data-dir", help="Custom data directory")

    # status
    status_p = sub.add_parser("status", help="Show pack and system status")
    status_p.add_argument("pack", nargs="?", default="coder", help="Pack name")
    status_p.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # verify
    verify_p = sub.add_parser("verify", help="Quick one-off validation")
    verify_p.add_argument("query", help="Query to validate")
    verify_p.add_argument("response", help="AI response to check")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "serve":
        _cmd_serve(args)
    elif args.command == "install-pack":
        _cmd_install_pack(args)
    elif args.command == "update-pack":
        _cmd_update_pack(args)
    elif args.command == "status":
        _cmd_status(args)
    elif args.command == "verify":
        _cmd_verify(args)


def _cmd_serve(args):
    import uvicorn
    print(f"Starting CertainLogic Verifier on {args.host}:{args.port}")
    uvicorn.run(
        "hallucination_guard.__main__:app",
        host=args.host,
        port=args.port,
    )


def _cmd_install_pack(args):
    from pathlib import Path
    from .packs import install_pack

    data_dir = Path(args.data_dir) if args.data_dir else None
    result = install_pack(
        pack_name=args.pack,
        license_key=args.key,
        data_dir=data_dir,
    )

    if result["status"] == "error":
        print(f"❌ {result['message']}")
        sys.exit(1)

    print(f"✅ {result['message']}")
    print()
    print("Next steps:")
    print(f"  1. Start the server:  hallucination-guard serve")
    if result["tier"] == "free":
        print(f"  2. Run sample queries to verify savings")
        print(f"  3. Upgrade for full pack: hallucination-guard install-pack {args.pack} --key YOUR_KEY")
    else:
        print(f"  2. Your system is production-ready — start building!")
        print(f"  3. Optional: hallucination-guard update-pack {args.pack}  (requires $9.99/mo subscription)")


def _cmd_update_pack(args):
    from pathlib import Path
    from .packs import update_pack

    data_dir = Path(args.data_dir) if args.data_dir else None
    result = update_pack(pack_name=args.pack, data_dir=data_dir)

    if result["status"] == "error":
        print(f"❌ {result['message']}")
        sys.exit(1)

    print(f"✅ {result['message']}")


def _cmd_status(args):
    from .packs import pack_status

    result = pack_status(pack_name=args.pack)

    if args.as_json:
        print(json.dumps(result, indent=2))
        return

    if not result.get("installed"):
        print(f"📦 Pack '{args.pack}': not installed")
        print(f"   Install: hallucination-guard install-pack {args.pack}")
        return

    tier_icon = "💎" if result.get("tier") == "paid" else "🆓"
    print(f"📦 Pack '{result['pack']}' {tier_icon}")
    print(f"   Tier:          {result.get('tier', 'unknown')}")
    print(f"   Facts:         {result.get('facts_count', '?')}")
    print(f"   Cache warmed:  {'✅' if result.get('cache_warmed') else '❌'}")
    print(f"   Cache entries: {result.get('cache_entries', 0)}")
    if result.get("version"):
        print(f"   Version:       {result['version']}")
    print(f"   Installed:     {result.get('installed_at', '?')}")
    if result.get("updated_at"):
        print(f"   Updated:       {result['updated_at']}")


def _cmd_verify(args):
    from .packs import get_active_facts_path
    from .hallucination_detector import HallucinationDetector

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
