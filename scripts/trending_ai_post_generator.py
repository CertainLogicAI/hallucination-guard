#!/usr/bin/env python3
"""
Auto-post trending AI take to X.
Generates 2 daily posts (10 AM and 3 PM CST) with CertainLogic perspective on hot AI stories.
"""

import json
import os
import subprocess
import urllib.request
import sys

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
CREDENTIALS = "/data/.openclaw/workspace/skills/x-api/scripts/.x-api.json"
SEEN_FILE = "/data/.openclaw/workspace/.seen_ai_stories.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_ai_stories():
    req = urllib.request.Request(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        headers={"User-Agent": "CertainLogic/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        top_ids = json.loads(resp.read().decode())[:50]
    
    stories = []
    seen = load_seen()
    for sid in top_ids:
        try:
            req2 = urllib.request.Request(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                headers={"User-Agent": "CertainLogic/1.0"}
            )
            with urllib.request.urlopen(req2, timeout=5) as r:
                s = json.loads(r.read().decode())
                title = s.get("title", "")
                url = s.get("url", "")
                if not title or sid in seen:
                    continue
                keywords = ["ai", "agent", "llm", "model", "gpt", "claude", "openai", "anthropic", "xai", "grok", "copilot"]
                if any(kw in title.lower() for kw in keywords):
                    stories.append({"id": sid, "title": title, "url": url or f"https://news.ycombinator.com/item?id={sid}"})
                    if len(stories) >= 3:
                        break
        except:
            continue
    return stories

def draft_post(story, slot):
    title = story["title"]
    url = story["url"]
    
    # If API key available, use LLM. Otherwise template.
    if API_KEY:
        try:
            msgs = [
                {"role": "system", "content": (
                    "You post for @CertainLogicAI on X. Voice: sharp, zero fluff, business-focused, "
                    "deterministic AI angle. Under 500 chars max. Add #DeterministicAI hashtag."
                )},
                {"role": "user", "content": (
                    f"Hot AI story: '{title}'. "
                    "Draft a take for business owners: what's the real implication? "
                    "Not a summary — a perspective. One concrete takeaway."
                )}
            ]
            payload = json.dumps({
                "model": "inclusionai/ling-2.6-flash:free",
                "messages": msgs,
                "max_tokens": 200,
                "temperature": 0.7
            }).encode()
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://certainlogic.ai"
                }
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read().decode())
                text = result["choices"][0]["message"]["content"].strip()
                if len(text) > 480:
                    text = text[:477] + "..."
                return text
        except Exception as e:
            print(f"LLM fallback: {e}")
    
    # Template fallback
    return (
        f"'{title}' — the AI space doesn't slow down.\n\n"
        "Business takeaway: every new capability needs an audit trail. "
        "If your agent can't prove what it did, you can't trust it.\n\n"
        "#DeterministicAI"
    )

def post_to_x(text):
    tweet_file = "/tmp/tweet_text.txt"
    with open(tweet_file, "w") as f:
        f.write(text)
    
    result = subprocess.run(
        ["node", "/data/.openclaw/workspace/skills/x-api/scripts/x-post-file.mjs",
         tweet_file],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr, result.returncode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=["morning", "afternoon"])
    args = parser.parse_args()
    
    stories = fetch_ai_stories()
    if not stories:
        print("No fresh AI stories found. Skipping.")
        sys.exit(0)
    
    seen = load_seen()
    story = stories[0]
    seen.add(story["id"])
    save_seen(seen)
    
    text = draft_post(story, args.slot)
    stdout, stderr, rc = post_to_x(text)
    
    if rc == 0:
        print(f"✅ Posted: {stdout.strip()}")
    else:
        print(f"❌ Failed: {stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
