#!/usr/bin/env python3
"""
Post Review Gate — Daily X Content Approval Workflow

Content engine generates 10 posts at 6 AM.
Anton reviews at start of day.
Only approved posts go out. Trending AI posts bypass review.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

APPROVAL_FILE = Path("/data/.openclaw/workspace/content_output/approved_slots.json")

def load_approvals():
    """Load today's approval state."""
    if APPROVAL_FILE.exists():
        data = json.load(open(APPROVAL_FILE))
        if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
            return set(data.get("approved", []))
    return set()

def save_approvals(approved_slots):
    """Save approval state for today."""
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "approved": sorted(list(approved_slots)),
        "updated_at": datetime.now().isoformat(),
    }
    APPROVAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(APPROVAL_FILE, "w"), indent=2)
    print(f"✅ Saved approvals: {approved_slots}")

def is_slot_approved(slot):
    """Check if a slot is approved for posting today."""
    approved = load_approvals()
    slot_map = {
        "morning": "morning", "morning_2": "morning",
        "midday": "midday", "midday_2": "midday_2",
        "evening": "evening", "evening_pre": "evening",
        "evening_2": "evening_2", "night": "evening_2",
    }
    canonical = slot_map.get(slot, slot)
    return canonical in approved

def approve_slot(slot):
    """Approve a single slot."""
    approved = load_approvals()
    approved.add(slot)
    save_approvals(approved)
    return True

def approve_all():
    """Approve all slots."""
    all_slots = {"morning", "midday", "midday_2", "evening", "evening_2"}
    save_approvals(all_slots)
    return True

def deny_slot(slot):
    """Revoke approval for a slot."""
    approved = load_approvals()
    approved.discard(slot)
    save_approvals(approved)
    return True

def show_todays_posts():
    """Display all posts for Anton to review."""
    today = datetime.now().strftime("%Y-%m-%d")
    posts_path = Path("/data/.openclaw/workspace/content_output") / f"x-posts-{today}.json"
    
    if not posts_path.exists():
        print(f"❌ No posts generated for {today}. Run: python3 marketing/content_engine.py")
        return None
    
    data = json.load(open(posts_path))
    posts = data.get("posts", [])
    approved = load_approvals()
    
    slot_map = {
        "morning": "🌅 8 AM (Posts 1-2)",
        "morning_2": "🌅 10 AM (Posts 3-4)",
        "midday": "☀️ 12 PM (Posts 5-6)",
        "midday_2": "☀️ 1 PM (Posts 7-8)",
        "evening": "🌆 4 PM (Post 9)",
        "evening_2": "🌙 5 PM (Post 10)",
    }
    
    print(f"\n# 📋 X Content Review — {today}")
    print(f"Generated: {data.get('generated_at', 'unknown')}")
    print(f"Brand: {data.get('brand', 'CertainLogic')}")
    print()
    
    # Group by slot
    slot_ranges = [
        ("morning", 0, 2, "🌅 8 AM"),
        ("morning_2", 2, 4, "🌅 10 AM"),
        ("midday", 4, 6, "☀️ 12 PM"),
        ("midday_2", 6, 8, "☀️ 1 PM"),
        ("evening", 8, 9, "🌆 4 PM"),
        ("evening_2", 9, 10, "🌙 5 PM"),
    ]
    
    for slot, start, end, label in slot_ranges:
        posts_in_slot = [p for p in posts if start < p["index"] <= end]
        status = "✅ APPROVED" if slot in approved else "⏳ PENDING"
        
        print(f"\n## {label} [{slot}] — {status}")
        for post in posts_in_slot:
            emoji = "✅" if post["under_limit"] else "⚠️"
            print(f"\n{emoji} Post {post['index']} — {post['emoji']} {post['type'].upper()} ({post['char_count']} chars)")
            print(f"```")
            print(post['text'])
            print(f"```")
    
    print(f"\n---")
    print(f"**Total:** {len(posts)} posts | **Approved slots:** {len(approved)}/5")
    print()
    print("**Commands:**")
    print(f"  Approve all:  `python3 marketing/post_review.py --approve-all`")
    print(f"  Approve slot: `python3 marketing/post_review.py --approve morning`")
    print(f"  Deny slot:    `python3 marketing/post_review.py --deny evening`")
    print(f"  Check status: `python3 marketing/post_review.py --status`")
    
    return posts

def show_status():
    """Quick status of approvals."""
    today = datetime.now().strftime("%Y-%m-%d")
    approved = load_approvals()
    
    slot_map = {
        "morning": "🌅 8 AM",
        "midday": "☀️ 12 PM",
        "midday_2": "☀️ 1 PM",
        "evening": "🌆 4 PM",
        "evening_2": "🌙 5 PM",
    }
    
    print(f"\n# 📊 Post Approval Status — {today}")
    for slot, label in slot_map.items():
        status = "✅ APPROVED" if slot in approved else "⏳ PENDING"
        print(f"  {label} [{slot}]: {status}")
    print(f"\n  **{len(approved)}/5 slots approved**")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="X Post Review Gate")
    parser.add_argument("--show", action="store_true", help="Display today's posts for review")
    parser.add_argument("--approve", help="Approve a slot (morning/midday/midday_2/evening/evening_2)")
    parser.add_argument("--deny", help="Deny/revoke approval for a slot")
    parser.add_argument("--approve-all", action="store_true", help="Approve all slots")
    parser.add_argument("--status", action="store_true", help="Show approval status")
    parser.add_argument("--check", help="Check if slot is approved (for scripts)")
    args = parser.parse_args()
    
    if args.show:
        show_todays_posts()
    elif args.approve:
        approve_slot(args.approve)
    elif args.deny:
        deny_slot(args.deny)
    elif args.approve_all:
        approve_all()
    elif args.status:
        show_status()
    elif args.check:
        print("approved" if is_slot_approved(args.check) else "pending")
    else:
        show_todays_posts()

if __name__ == "__main__":
    main()
