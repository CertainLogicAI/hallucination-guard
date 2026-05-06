#!/usr/bin/env python3
"""
Trend Skill Factory — Autonomous Free Skill Builder
Monitors trends, researches with deep subagents, and builds skills.
Uses ONLY free models via OpenRouter. 100% monitored. Fully auditable.

Mobile: Querying Brain API for existing skills + market gaps.
Desktop: Running as cron, building skills for ClawHub.
"""

import subprocess, json, sys, os, time, datetime, uuid
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────
CONFIG = {
    "mode": "manual",      # "manual" = review before any action | "auto" = full autonomy
    "dry_run": True,       # True = simulate, False = actually build/publish
    "max_skills_per_day": 3,
    "research_depth": "deep",  # "quick" or "deep" controls subagent spawn

    "models": {
        "research": "deepseek/deepseek-chat-v3-0324:free",     # Best free reasoning model
        "coding": "qwen/qwen3-coder:free",                     # Best free coding model  
        "fallback": "inclusionai/ling-2.6-flash:free",          # Fast fallback
    },

    "brain_api": "http://127.0.0.1:8000",
    "output_dir": "artifacts/auto-skills",
    "log_file": "logs/trend_factory.jsonl",
    "metrics_file": "logs/trend_factory_metrics.jsonl",
}

# ── MONITORING ──────────────────────────────────────────────────────────
class FactoryMonitor:
    STATUS = {
        "runs": 0, "skills_built": 0, "skills_published": 0,
        "errors": 0, "tokens_used": 0, "cost_incurred": 0.0,
        "last_run": None
    }

    @classmethod
    def log(cls, topic: str, stage: str, success: bool, details: dict = None):
        entry = {
            "_ts": time.time(), "_id": str(uuid.uuid4())[:8], "topic": topic, "stage": stage,
            "success": success, "details": details or {}, "status": cls.STATUS.copy(),
        }
        cls.write(entry)
        return cls.print(entry)

    @classmethod
    def write(cls, entry: dict):
        os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
        with open(CONFIG["log_file"], "a") as f:
            f.write(json.dumps(entry) + "\n")

    @classmethod
    def write_metrics(cls):
        os.makedirs(os.path.dirname(CONFIG["metrics_file"]), exist_ok=True)
        with open(CONFIG["metrics_file"], "a") as f:
            f.write(json.dumps({"_ts": time.time(), **cls.STATUS}) + "\n")

    @classmethod
    def print(cls, entry: dict):
        ts = datetime.datetime.fromtimestamp(entry["_ts"]).strftime("%H:%M:%S")
        ok = "✅" if entry["success"] else "❌"
        print(f"[{ts}] {ok} {entry['stage']:12} | {entry['topic'][:40]:40} | run={entry['status']['runs']}")

    @classmethod
    def error(cls, topic: str, stage: str, error: str):
        cls.STATUS["errors"] += 1
        Status = cls.log(topic, stage, False, {"error": error})
        return Status

# ── BRAIN API ──────────────────────────────────────────────────────────
class BrainAPI:
    @classmethod
    def ask(cls, query: str, max_results: int = 3) -> list:
        """Query our deterministic brain for existing skills/context."""
        try:
            import requests
            r = requests.post(f"{CONFIG['brain_api']}/search", json={"query": query, "n": max_results}, timeout=10)
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception as e:
            FactoryMonitor.error("brain_api", "search", str(e))
            return []

    @classmethod
    def check_skill_exists(cls, skill_slug: str) -> bool:
        """Check if we already built a skill for this."""
        try:
            import requests
            r = requests.post(f"{CONFIG['brain_api']}/query", json={"question": f"Is there a skill called {skill_slug}?"}, timeout=10)
            r.raise_for_status()
            return "yes" in r.json().get("answer", "").lower()
        except:
            return False

# ── FREE MODEL ROUTER ───────────────────────────────────────────────────
class FreeModel:
    OPENROUTER_KEY = None
    
    @classmethod
    def load_key(cls):
        if cls.OPENROUTER_KEY:
            return cls.OPENROUTER_KEY
        try:
            with open("/data/.openclaw/secrets/openrouter.json") as f:
                cls.OPENROUTER_KEY = json.load(f)["api_key"]
            return cls.OPENROUTER_KEY
        except:
            # Fallback to env
            cls.OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
            return cls.OPENROUTER_KEY

    @classmethod
    def call(cls, model: str, system: str, prompt: str, task_type: str = "research") -> dict:
        """Call free model via OpenRouter. 100% audit logged."""
        key = cls.load_key()
        if not key:
            return {"error": "No OpenRouter key", "content": ""}

        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3 if task_type == "coding" else 0.7,
            "max_tokens": 4000,
        }

        start = time.time()
        try:
            import requests
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={
                "Authorization": f"Bearer {key}",
                "HTTP-Referer": "https://certainlogic.ai",
                "X-Title": "CertainLogic-TrendFactory",
                "Content-Type": "application/json",
            }, json=body, timeout=120)
            r.raise_for_status()
            data = r.json()
            latency = round(time.time() - start, 2)
            
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            result = {
                "model": model, "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0), 
                "latency": latency, "content": content, "success": True,
            }
            
            # Track cost (all models are free = $0, but we track for reporting)
            FactoryMonitor.STATUS["tokens_used"] += usage.get("total_tokens", 0)
            FactoryMonitor.STATUS["cost_incurred"] += 0.0  # Free models
            
            FactoryMonitor.log("model_call", f"{task_type}_generation", True, result)
            return result
            
        except Exception as e:
            FactoryMonitor.error("model_call", f"{task_type}_generation", str(e))
            return {"error": str(e), "content": "", "success": False}

# ── TREND SOURCES ───────────────────────────────────────────────────────
class TrendSource:
    SOURCES = {
        "reddit": [
            "https://www.reddit.com/r/selfhosted/hot.json?limit=5",
            "https://www.reddit.com/r/LocalLLaMA/hot.json?limit=5",
            "https://www.reddit.com/r/ClaudeAI/hot.json?limit=5",
        ],
        "news": [
            "https://hnrss.org/newest?q=AI+agent",  # Hacker News
        ]
    }

    @classmethod
    def fetch_trending_topics(cls) -> list:
        """Fetch raw trending topics. Light scraping."""
        topics = []
        try:
            import requests
            for url in cls.SOURCES["reddit"]:
                try:
                    r = requests.get(url, headers={"User-Agent": "CertainLogic-Bot/1.0"}, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        for post in data.get("data", {}).get("children", [])[:3]:
                            t = post.get("data", {})
                            topic = t.get("title", "")
                            if len(topic) > 20 and t.get("score", 0) > 10:
                                topics.append({
                                    "title": topic, "source": "reddit", "score": t.get("score"),
                                    "url": f"https://reddit.com{t.get('permalink', '')}",
                                    "text": t.get("selftext", "")[:500]
                                })
                except:
                    continue
        except Exception as e:
            FactoryMonitor.error("trends", "fetch", str(e))
        return topics

# ── DEEP RESEARCH SUBAGENT ──────────────────────────────────────────────
class ResearchSubagent:
    """Spawns subagent for deep research on a trend topic."""

    @classmethod
    def research(cls, topic: dict) -> dict:
        """Use the BEST free reasoning model to deep research a topic."""
        system = """You are a market intelligence analyst specializing in AI agent tooling.
        Given a trending topic, analyze:
        1. Is there a real user pain point here?
        2. What existing tools address this? What are their gaps?
        3. What would a skill/tool look like that solves this cleanly?
        4. Uniqueness score (1-10): How differentiated would our solution be?
        5. Build vs. not: Should we build this as a free ClawHub skill?
        
        Respond in structured JSON only."""

        prompt = f"""Topic: {topic['title']}
Source: {topic['source']} (score: {topic.get('score','?')})
Description: {topic.get('text','')[:300]}

OUR CONTEXT:
- We build deterministic AI tools (CertainLogic)
- Free tier: OpenClaw skills on ClawHub
- Premium: Company Brain infrastructure
- Current free skills: {', '.join(['pathfinder', 'skill-guard', 'skill-vetter-plus', 'skill-oracle'])}

Analyze if we should build a skill for this. Return JSON with fields:
pain_point, existing_tools, gap_analysis, solution_sketch, uniqueness_score, build_decision, reasoning
"""
        return FreeModel.call(CONFIG["models"]["research"], system, prompt, task_type="research")

# ── SKILL BUILDER ───────────────────────────────────────────────────────
class SkillBuilder:
    @classmethod
    def build_skill(cls, research: dict, topic: dict) -> dict:
        """Use best free coding model to generate the skill."""
        system = """You are a senior developer building OpenClaw AgentSkills.
        Each skill is a folder with:
        - SKILL.md (how-tos and when the skill triggers)
        - skill.json (metadata)
        - scripts/ (Python or JS implementation files)
        
        Rules:
        - Simple, single-purpose skills are better than complex ones
        - Every skill must have a clear "read_when" trigger condition
        - Scripts must be self-contained, no external dependencies beyond Python stdlib
        - Include error handling
        - NO PLACEHOLDERS. Build real, working code.
        """

        prompt = f"""Build a working OpenClaw skill for this opportunity:

PAIN POINT: {research['pain_point']}
GAP: {research['gap_analysis']}
SOLUTION SKETCH: {research['solution_sketch']}

Requirements:
1. Create a concise SKILL.md describing what it does and when to use it
2. Create skill.json with unique id (format: certainlogicai.skill-name)
3. Create at least one working script in scripts/
4. Make it self-contained and immediately usable

Respond with the complete file tree as JSON:
{{
    "skill_id": "certainlogicai.unique-name",
    "files": {{
        "SKILL.md": "content...",
        "skill.json": "content...",
        "scripts/main.py": "content..."
    }}
}}"""
        return FreeModel.call(CONFIG["models"]["coding"], system, prompt, task_type="coding")

# ── MAIN PIPELINE ───────────────────────────────────────────────────────
class TrendFactory:
    @classmethod
    def run(cls, max_topics: int = 3):
        FactoryMonitor.STATUS["runs"] += 1
        FactoryMonitor.STATUS["last_run"] = time.time()
        
        print(f"{'='*60}")
        print(f"  Trend Skill Factory v1.0 — {datetime.datetime.now().isoformat()}")
        print(f"  Mode: {CONFIG['mode']} | Dry run: {CONFIG['dry_run']}")
        print(f"  Reasoning: {CONFIG['models']['research']} | Coding: {CONFIG['models']['coding']}")
        print(f"{'='*60}\n")

        # 1. Get trends
        trends = TrendSource.fetch_trending_topics()
        print(f"📊 Fetched {len(trends)} trending topics\n")
        if not trends:
            print("⚠️  No trends found. Aborting.")
            FactoryMonitor.write_metrics()
            return

        # 2. Check against brain
        for t in trends[:max_topics]:
            title_safe = t['title'][:40].replace(" ", "_").replace("/", "_")
            print(f"🔍 Topic: {t['title'][:60]}...")
            
            existing = BrainAPI.ask(f"Is there a skill for {t['title']}?")
            if existing and any("skill" in str(e).lower() for e in existing):
                print(f"   ⏭️  Already have skill in this space")
                FactoryMonitor.log(title_safe, "existing_check", True, {"found": True})
                continue

            # 3. Deep research
            print(f"   🧠 Deep researching with {CONFIG['models']['research']}...")
            research = ResearchSubagent.research(t)
            if not research.get("content"):
                print(f"   ❌ Research failed")
                continue
            
            try:
                parsed = json.loads(research["content"].replace("```json", "").replace("```", "").strip())
                score = int(parsed.get("uniqueness_score", 0))
                build = parsed.get("build_decision", "no").lower()
                print(f"   ✅ Research: uniqueness={score}/10, decision={build}")
            except:
                print(f"   ⚠️  Could not parse research JSON, skipping")
                continue

            if build != "yes" or score < 6:
                print(f"   ⏭️  Decision: DON'T BUILD (score={score})")
                FactoryMonitor.log(title_safe, "build_gate", False, {"score": score, "decision": build})
                continue

            print(f"   🏗️  BUILDING skill with {CONFIG['models']['coding']}...")
            skill_code = SkillBuilder.build_skill(parsed, t)
            if not skill_code.get("content"):
                print(f"   ❌ Build failed")
                continue

            # 4. Write files
            if CONFIG["dry_run"]:
                print(f"   ✨ DRY RUN — would write {len(skill_code['content'])} chars of skill code")
                print(f"   📁 Would create: artifacts/auto-skills/{title_safe}/")
                FactoryMonitor.log(title_safe, "dry_run_build", True, {"chars": len(skill_code['content'])})
            else:
                os.makedirs(f"{CONFIG['output_dir']}/{title_safe}", exist_ok=True)
                try:
                    skill_json = json.loads(skill_code["content"].replace("```json", "").replace("```", "").strip())
                    for path, content in skill_json.get("files", {}).items():
                        out_path = f"{CONFIG['output_dir']}/{title_safe}/{path}"
                        os.makedirs(os.path.dirname(out_path), exist_ok=True)
                        with open(out_path, "w") as f:
                            f.write(content)
                    print(f"   ✅ Built: {CONFIG['output_dir']}/{title_safe}/")
                    FactoryMonitor.STATUS["skills_built"] += 1
                    FactoryMonitor.log(title_safe, "build", True, {"path": f"{CONFIG['output_dir']}/{title_safe}"})
                except Exception as e:
                    FactoryMonitor.error(title_safe, "build_file", str(e))

        FactoryMonitor.write_metrics()
        print(f"\n🏁 Run complete. Skills built: {FactoryMonitor.STATUS['skills_built']}/{max_topics}")
        print(f"📊 Full log: {CONFIG['log_file']}")

# ── CLI ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or CONFIG["dry_run"]
    limit = 1
    for arg in sys.argv[1:]:
        if arg.startswith("--max-topics="):
            limit = int(arg.split("=")[1])
    
    CONFIG["dry_run"] = dry
    print(f"DRY RUN: {dry} | Topics: {limit}\n")
    TrendFactory.run(max_topics=limit)
