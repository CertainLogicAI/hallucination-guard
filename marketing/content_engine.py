#!/usr/bin/env python3
"""
CertainLogic Content Engine — Daily X Post Generator
Generates 10 brand-aligned X posts with the HSCR framework.

Post-Phase-4D Migration:
  - Queries Brain for brand voice/strategy to weight template selection
  - Falls back to legacy random selection if Brain unavailable
  - Zero changes to output format or CLI

Usage: python3 content_engine.py [--date YYYY-MM-DD] [--output-dir PATH]
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Brain Integration (Phase 4D) ────────────────────────────────────────────

# Optional brain import — wrapped in try/except for graceful fallback
def _load_brain():
    """Lazy-load Brain wrapper. Returns None if unavailable."""
    try:
        # Add company-brain to Python path
        brain_path = Path("/data/.openclaw/workspace/company-brain")
        if str(brain_path) not in sys.path:
            sys.path.insert(0, str(brain_path))
        from brain_wrapper import Brain
        return Brain()
    except Exception:
        return None

_BRAIN = None  # Lazy singleton

def get_brain():
    """Get or create Brain singleton."""
    global _BRAIN
    if _BRAIN is None:
        _BRAIN = _load_brain()
    return _BRAIN

def get_brain_messaging_themes():
    """
    Query brain for current messaging priorities.
    Returns weighted theme map, or None if brain unavailable.
    """
    brain = get_brain()
    if brain is None:
        return None

    # Query multiple axes and merge scores
    weighted = {}

    try:
        # Strategy positioning
        strategy = brain.strategy("what is our brand messaging today")
        if strategy.get("confidence", 0) > 0.2:
            weighted["strategy"] = strategy["confidence"]
    except Exception:
        pass

    try:
        # Product highlight
        product = brain.product("what product should we highlight")
        if product.get("confidence", 0) > 0.2:
            weighted["product"] = product["confidence"]
    except Exception:
        pass

    try:
        # Operational message
        ops = brain.ops("what is our current focus")
        if ops.get("confidence", 0) > 0.2:
            weighted["ops"] = ops["confidence"]
    except Exception:
        pass

    return weighted if weighted else None

def get_brain_quote():
    """
    Pull a quote or key line from brain if available.
    Returns (text, confidence) or (None, 0).
    """
    brain = get_brain()
    if brain is None:
        return None, 0

    try:
        result = brain.query("brand voice quote or key message today")
        if result.get("confidence", 0) > 0.2:
            return result.get("answer", ""), result.get("confidence", 0)
    except Exception:
        pass

    return None, 0


# ─── Load Inventory (Single Source of Truth) ──────────────────────────────────

def load_inventory():
    """Load product counts from brain_inventory.json."""
    inventory_path = "/data/.openclaw/workspace/brain_inventory.json"
    try:
        with open(inventory_path, 'r') as f:
            inv = json.load(f)
        products = inv.get('products', {}).get('coding_agent_pro', {})
        return {
            'facts': products.get('total_facts', 338),
            'queries': products.get('total_query_mappings', 1014),
            'version': products.get('version', '1.0.0'),
        }
    except Exception:
        return {'facts': 338, 'queries': 1014, 'version': '1.0.0'}

INVENTORY = load_inventory()

# ─── Brand Voice & Identity ───────────────────────────────────────────────────

BRAND = {
    "name": "CertainLogicAI",
    "handle": "@CertainLogicAI",
    "site": "certainlogic.ai",
    "creator": "Alex",
    "emoji": "⚡",
    "voice": [
        "Sharp, direct, zero fluff",
        "Controls engineering mindset applied to AI",
        "Real numbers > marketing copy",
        "Unpopular opinions welcome",
        "Builds in public",
    ],
    "products": {
        "agentpathfinder": {
            "name": "AgentPathfinder",
            "description": "Signed task tracking for AI agents — records and audits claims",
            "downloads": 185,
            "url": "clawhub.com",
        },
        "deterministic_ai": {
            "name": "Deterministic AI Layer",
            "description": "Cached responses, facts lookup, uncertainty flagging",
            "savings": "85%",
        },
        "coding_agent": {
            "name": "Coding Agent Pro",
            "description": f"{INVENTORY['facts']} verified coding facts with query coverage",
            "facts": INVENTORY['facts'],
            "queries": INVENTORY['queries'],
        },
    },
    "themes": [
        "ai_reliability",
        "deterministic_vs_probabilistic",
        "cost_reduction",
        "build_in_public",
        "industrial_automation",
        "business_ai_strategy",
        "cofounder_journey",
        "beta_feedback",
    ],
}

# ─── Post Templates by Type ───────────────────────────────────────────────────

TEMPLATES = {
    "hook": [
        {
            "text": "I spent 15 years in industrial automation learning that unreliable systems cost money.\n\nThen I started using AI tools in business and saw the same problem — confident, wrong answers with no accountability.\n\nSo I built the fix.\n\nBuilding @CertainLogicAI in public. Follow along.",
            "cta": "Follow for weekly builds",
            "emoji": "🪝",
        },
        {
            "text": "Most AI 'solutions' sold to small businesses are general-purpose models dressed up in a custom UI.\n\nThe model doesn't know your prices, your policies, or your business.\n\nIt's guessing. Confidently.",
            "cta": "Follow for the alternative",
            "emoji": "🪝",
        },
        {
            "text": "Hot take: 'AI-powered' is becoming a red flag.\n\nIt signals: probabilistic, unverifiable, unreliable.\n\n'Deterministic' will be the new trust signal for business applications.\n\nSame shift that happened with 'cloud' → 'enterprise cloud.'",
            "cta": "Agree or disagree?",
            "emoji": "🔥",
        },
        {
            "text": "Confidence ≠ correctness.\n\nThe most dangerous AI answers are the ones that sound certain.\n\nA model that says 'I'm not sure' is safer than one that makes something up fluently.\n\nMost business AI is optimized for fluency, not accuracy.",
            "cta": "Reply with your experience",
            "emoji": "🎯",
        },
        {
            "text": "The AI divide isn't coming. It's here.\n\nBusinesses using AI effectively are already operating at a different level than those that aren't.\n\nThe gap compounds every month.",
            "cta": "Which side are you on?",
            "emoji": "⚡",
        },
    ],
    "proof": [
        {
            "text": "How I cut AI API costs by up to 85%:\n\n→ Cache answers after first response (same question = free)\n→ Compress inputs before they hit the model\n→ Hard cap on output length (reduces cost + hallucination surface)\n\nSimple system. Significant savings. Results vary by workload.",
            "cta": "Want the full breakdown?",
            "emoji": "📊",
        },
        {
            "text": "AgentPathfinder just crossed 185 downloads on ClawHub.\n\nBuilt in public. Zero ad spend. Zero influencer budget.\n\nJust a problem worth solving and a build log anyone can follow.\n\nProof that deterministic AI resonates.",
            "cta": "Try it: clawhub.com",
            "emoji": "📈",
        },
        {
            "text": "Our token reduction system hit up to 38% cache hit rate on measured workloads.\n\nThat means up to 38% of AI queries cost $0.\n\nSame answer quality. Faster than LLM calls — returns in ~100ms vs. 1-4 seconds.\n\nThe system gets cheaper and faster the more you use it. That's the opposite of most AI infrastructure.",
            "cta": "See how it works",
            "emoji": "💰",
        },
        {
            "text": f"Coding Agent Pro now covers {INVENTORY['facts']} verified facts with {INVENTORY['queries']} query patterns.\n\nFrom Python basics to AWS infrastructure to security standards.\n\nEvery query pulls from a curated database — not training data guesses.\n\nSame answer every time. That's what cached facts look like in practice.",
            "cta": "Read the build log",
            "emoji": "🧠",
        },
    ],
    "lesson": [
        {
            "text": "Lesson from this week:\n\nOld content system: single-digit views\nNew Grok pipeline: 41 views immediately\n\nThe lesson: quality of thought > quantity.\n\nOne sharp post beats ten mediocre ones.\n\nWould've saved me weeks of low engagement.",
            "cta": "What did you learn this week?",
            "emoji": "💡",
        },
        {
            "text": "What makes a good AI tool for business (vs a bad one):\n\nBad:\n→ Answers from training data\n→ No audit trail\n→ Confident when wrong\n→ Unpredictable costs\n\nGood:\n→ Answers from your verified data\n→ Full audit trail\n→ Flags uncertainty\n→ Predictable, capped costs",
            "cta": "Save this checklist",
            "emoji": "✅",
        },
        {
            "text": "The controls engineering mindset applied to AI:\n\n→ Define failure modes before deployment\n→ Build in fallbacks\n→ Make it auditable\n→ Assume it will fail at the worst time\n→ Design for that\n\nMost AI deployments skip all of this. Then act surprised when something goes wrong.",
            "cta": "Engineers will understand",
            "emoji": "🔧",
        },
        {
            "text": "What 'AI automation' looks like for small biz:\n\nNot: a robot that does everything\n\nActually:\n→ Specific process, defined I/O\n→ Verified data source\n→ Human reviews edge cases\n→ Clear escalation path\n→ Measurable time savings\n\nStart narrow. Prove it works. Expand.",
            "cta": "Tag a business owner",
            "emoji": "🏗️",
        },
    ],
    "engagement": [
        {
            "text": "Question for business owners:\n\nHave you ever caught your AI tool giving a customer wrong information?\n\nWhat happened?\n\nI'll go first: our old chatbot quoted a pricing tier that didn't exist. Customer was confused. We looked unprofessional. Never again.",
            "cta": "Reply with your story",
            "emoji": "💬",
        },
        {
            "text": "Genuinely curious:\n\nWhat's the most expensive mistake an AI tool has made for you or your business?\n\nNo judgment. Trying to understand the real failure modes.\n\nI'll share mine in the replies.",
            "cta": "Drop it below 👇",
            "emoji": "🤔",
        },
        {
            "text": "For any AI tool you're evaluating, ask this:\n\n'What happens when it doesn't know the answer?'\n\nIf it says 'provides a best estimate' — it guesses.\n\nIf it says 'escalates to a human' — it's built for reliability.\n\nThat question cuts through 90% of vendor noise.",
            "cta": "Save this for your next demo",
            "emoji": "🧐",
        },
    ],
    "recap": [
        {
            "text": "Week in numbers:\n\n🐦 Impressions: building\n👀 AgentPathfinder: 185 downloads\n💰 AI cost cut: up to 85% (workload dependent)\n📦 Systems shipped: 3\n🔥 Best: Grok content pipeline\n\nReflection: cached answers message is landing.",
            "cta": "Follow the build",
            "emoji": "📊",
        },
    ],
}

# ─── Engine ───────────────────────────────────────────────────────────────────

class ContentEngine:
    def __init__(self, date_str: str | None = None):
        self.date = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.posts: list[dict] = []

    def _format_post(self, template: dict, index: int, post_type: str) -> dict:
        """Format a single post with metadata."""
        text = template["text"].strip()
        cta = template.get("cta", "").strip()
        emoji = template.get("emoji", "⚡")
        
        # Ensure under 280 chars for main tweet
        char_count = len(text)
        
        post = {
            "index": index + 1,
            "type": post_type,
            "emoji": emoji,
            "text": text,
            "cta": cta,
            "char_count": char_count,
            "under_limit": char_count <= 280,
            "hashtags": [],
            "schedule_time": None,
        }
        return post

    def generate_daily_posts(self, count: int = 10) -> list[dict]:
        """Generate N posts for the day with variety.

        Phase 4D Enhancement: Uses brain insights to weight type selection.
        Falls back to legacy behavior if brain unavailable.
        """
        # Brain-enhanced type weights (or legacy uniform)
        brain_themes = get_brain_messaging_themes()
        if brain_themes and "strategy" in brain_themes:
            # Brain has a strong strategy message — weight proof/lesson higher
            type_pool = (
                ["hook"] * 2 +
                ["proof"] * 4 +
                ["lesson"] * 3 +
                ["engagement"] * 2 +
                ["recap"] * 1
            )
        elif brain_themes and "product" in brain_themes:
            # Brain wants product highlight — weight proof higher
            type_pool = (
                ["hook"] * 3 +
                ["proof"] * 5 +
                ["lesson"] * 2 +
                ["engagement"] * 2 +
                ["recap"] * 1
            )
        else:
            # Legacy: balanced distribution
            type_pool = (
                ["hook"] * 3 +
                ["proof"] * 3 +
                ["lesson"] * 2 +
                ["engagement"] * 2 +
                ["recap"] * 1
            )

        # Optionally inject brain quote into a hook post
        brain_quote, _ = get_brain_quote()

        used_templates: set[tuple[str, int]] = set()
        brain_quote_used = False

        for i in range(count):
            # Pick a type, avoiding immediate repeats if possible
            available_types = [t for t in type_pool if t not in [p["type"] for p in self.posts[-2:]]] or type_pool
            post_type = random.choice(available_types)

            # Pick a template we haven't used
            templates = TEMPLATES[post_type]
            available_indices = [j for j in range(len(templates)) if (post_type, j) not in used_templates]
            if not available_indices:
                available_indices = list(range(len(templates)))

            idx = random.choice(available_indices)
            used_templates.add((post_type, idx))

            post = self._format_post(templates[idx], i, post_type)

            # Phase 4D: if this is a hook post and we have a brain quote, prepend it
            if post_type == "hook" and brain_quote and not brain_quote_used:
                brain_quote_used = True
                brain_line = brain_quote.split("\n")[0][:200]  # First line, max 200 chars
                post["text"] = f"{brain_line}\n\n{post['text']}"
                post["brain_enhanced"] = True
                post["char_count"] = len(post["text"])
                post["under_limit"] = post["char_count"] <= 280

            self.posts.append(post)

        return self.posts

    def to_markdown(self) -> str:
        """Render posts as a markdown document."""
        lines = [
            f"# CertainLogic Daily X Content — {self.date}",
            f"Generated: {datetime.now(timezone.utc).isoformat()} UTC",
            f"Brand: {BRAND['name']} ({BRAND['handle']})",
            f"Voice: {', '.join(BRAND['voice'][:2])}",
            "",
            "---",
            "",
        ]
        
        for post in self.posts:
            status = "✅" if post["under_limit"] else "⚠️ OVER LIMIT"
            lines.extend([
                f"## Post {post['index']} — {post['emoji']} {post['type'].upper()} {status}",
                "",
                f"**Char count:** {post['char_count']}/280",
                "",
                "```",
                post["text"],
                "```",
                "",
                f"**CTA:** {post['cta']}" if post['cta'] else "",
                "",
                "---",
                "",
            ])
        
        # Summary stats
        under_limit = sum(1 for p in self.posts if p["under_limit"])
        lines.extend([
            "## Summary",
            "",
            f"- **Total posts:** {len(self.posts)}",
            f"- **Under 280 chars:** {under_limit}/{len(self.posts)}",
            f"- **Types:** {', '.join(set(p['type'] for p in self.posts))}",
            "",
            "Post via: `scripts/tweet.sh \"Your text here\"`",
            "",
        ])
        
        return "\n".join(lines)

    def to_json(self) -> str:
        """Export posts as JSON for API consumption."""
        return json.dumps({
            "date": self.date,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "brand": BRAND["name"],
            "posts": self.posts,
        }, indent=2)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CertainLogic Content Engine")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--output-dir", help="Output directory", default="/data/.openclaw/workspace/content_output")
    parser.add_argument("--count", type=int, help="Number of posts", default=10)
    parser.add_argument("--format", choices=["md", "json", "both"], default="both")
    args = parser.parse_args()

    engine = ContentEngine(date_str=args.date)
    posts = engine.generate_daily_posts(count=args.count)

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    files_written = []
    
    if args.format in ("md", "both"):
        md_path = os.path.join(args.output_dir, f"x-posts-{engine.date}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(engine.to_markdown())
        files_written.append(md_path)
        print(f"✅ Markdown: {md_path}")

    if args.format in ("json", "both"):
        json_path = os.path.join(args.output_dir, f"x-posts-{engine.date}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(engine.to_json())
        files_written.append(json_path)
        print(f"✅ JSON: {json_path}")

    # Console summary
    print(f"\n📊 Generated {len(posts)} posts for {engine.date}")
    for p in posts:
        status = "✅" if p["under_limit"] else "⚠️"
        print(f"  {status} Post {p['index']:2d} | {p['emoji']} {p['type']:12s} | {p['char_count']:3d} chars")

    return 0


if __name__ == "__main__":
    sys.exit(main())
