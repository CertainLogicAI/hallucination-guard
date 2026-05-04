#!/usr/bin/env python3
"""
CertainLogic X Poster — Permanent credential storage
Reads from ~/.openclaw/workspace/secrets/x_credentials.json (survives sessions)
Falls back to environment variables
Posts content either from today's generated file or command line
"""
import json, os, sys, random
from datetime import datetime
from pathlib import Path

# ─── Credential Loading ─────────────────────────────────────────────

def load_x_credentials():
    """Load X API credentials from permanent file or env vars."""
    # Primary: permanent file (survives session compaction)
    creds_path = Path.home() / ".openclaw" / "workspace" / "secrets" / "x_credentials.json"
    if creds_path.exists():
        try:
            data = json.load(open(creds_path))
            api_key = data.get("api_key", data.get("consumer_key", ""))
            api_secret = data.get("api_secret", data.get("consumer_secret", ""))
            access_token = data.get("access_token", data.get("accessToken", ""))
            access_secret = data.get("access_token_secret", data.get("accessTokenSecret", ""))
            
            if api_key and api_secret and access_token and access_secret:
                if "YOUR_" in api_key:
                    print("⚠️  Credentials file has placeholders. Run:\n   nano ~/.openclaw/workspace/secrets/x_credentials.json")
                    return None
                return {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "access_token": access_token,
                    "access_secret": access_secret,
                }
        except Exception as e:
            print(f"❌ Failed to read credentials file: {e}")
    
    # Fallback: environment variables
    env_creds = {
        "api_key": os.environ.get("X_API_KEY", os.environ.get("CONSUMER_KEY", "")),
        "api_secret": os.environ.get("X_API_SECRET", os.environ.get("CONSUMER_SECRET", "")),
        "access_token": os.environ.get("X_ACCESS_TOKEN", os.environ.get("ACCESS_TOKEN", "")),
        "access_secret": os.environ.get("X_ACCESS_SECRET", os.environ.get("ACCESS_SECRET", "")),
    }
    if all(env_creds.values()):
        return env_creds
    
    print("""❌ No X API credentials found.

Primary source (permanent):
  ~/.openclaw/workspace/secrets/x_credentials.json

Fallback (env vars):
  export X_API_KEY="..."
  export X_API_SECRET="..."
  export X_ACCESS_TOKEN="..."
  export X_ACCESS_SECRET="..."
""")
    return None

# ─── Post to X ──────────────────────────────────────────────────────

def post_to_x(text: str, dry_run: bool = False):
    """Post text to X using OAuth 1.0a."""
    creds = load_x_credentials()
    if not creds:
        return False
    
    if dry_run:
        print(f"[DRY RUN] Would post:\n{text}")
        return True
    
    try:
        import tweepy
        auth = tweepy.OAuthHandler(creds["api_key"], creds["api_secret"])
        auth.set_access_token(creds["access_token"], creds["access_secret"])
        client = tweepy.API(auth)
        
        # Try v2 API first
        client_v2 = tweepy.Client(
            consumer_key=creds["api_key"],
            consumer_secret=creds["api_secret"],
            access_token=creds["access_token"],
            access_token_secret=creds["access_secret"]
        )
        
        response = client_v2.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"✅ Posted: https://x.com/i/status/{tweet_id}")
        return True
        
    except ImportError:
        # Fallback to simple OAuth1 request with requests
        import requests, urllib.parse, hmac, hashlib, base64, time
        
        def sign_request(url, method, params, consumer_secret, token_secret):
            params_string = "&".join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}" 
                                      for k, v in sorted(params.items()))
            base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(params_string, safe='')}"
            signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
            signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
            return signature
        
        url = "https://api.twitter.com/2/tweets"
        timestamp = str(int(time.time()))
        nonce = base64.b64encode(os.urandom(16)).decode().rstrip("=")
        
        oauth_params = {
            "oauth_consumer_key": creds["api_key"],
            "oauth_nonce": nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": timestamp,
            "oauth_token": creds["access_token"],
            "oauth_version": "1.0",
        }
        
        oauth_params["oauth_signature"] = sign_request(url, "POST", oauth_params, creds["api_secret"], creds["access_secret"])
        
        auth_header = "OAuth " + ", ".join(f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"' 
                                              for k, v in oauth_params.items())
        
        response = requests.post(url, headers={"Authorization": auth_header, "Content-Type": "application/json"}, 
                                json={"text": text})
        
        if response.status_code == 201:
            data = response.json()
            tweet_id = data["data"]["id"]
            print(f"✅ Posted: https://x.com/i/status/{tweet_id}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return False

# ─── Content Loading ────────────────────────────────────────────────

def load_todays_post(slot: str = None):
    """Load today's generated posts and pick one, optionally by slot."""
    today = datetime.now().strftime("%Y-%m-%d")
    posts_path = Path("/data/.openclaw/workspace/content_output") / f"x-posts-{today}.json"
    
    if not posts_path.exists():
        print(f"❌ No posts generated for {today}. Run: python3 marketing/content_engine.py")
        return None
    
    data = json.load(open(posts_path))
    posts = data.get("posts", [])
    
    if not posts:
        print("❌ No posts in today's file")
        return None
    
    # Slot-based selection
    slot_map = {
        "morning": (0, 2),     # Posts 1-2
        "morning_2": (2, 4),   # Posts 3-4
        "midday": (4, 6),      # Posts 5-6
        "midday_2": (6, 8),    # Posts 7-8
        "evening": (8, 9),     # Post 9
        "evening_pre": (8, 9), # Post 9
        "evening_2": (9, 10),  # Post 10
        "night": (9, 10),      # Post 10
    }
    
    if slot and slot in slot_map:
        start, end = slot_map[slot]
        candidates = [p for p in posts if start <= p["index"] - 1 < end]
    else:
        # Pick first un-posted hook/proof/engagement
        candidates = [p for p in posts if p["type"] in ("hook", "proof", "engagement")]
    
    if not candidates:
        candidates = posts
    
    return random.choice(candidates)

# ─── CLI ────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CertainLogic X Poster")
    parser.add_argument("--text", help="Post this text directly")
    parser.add_argument("--slot", help="Pick from slot: morning/morning_2/midday/midday_2/evening/evening_pre/evening_2/night")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be posted but don't post")
    parser.add_argument("--list", action="store_true", help="Show today's available posts")
    args = parser.parse_args()
    
    if args.list:
        post = load_todays_post()
        if post:
            today = datetime.now().strftime("%Y-%m-%d")
            posts_path = Path("/data/.openclaw/workspace/content_output") / f"x-posts-{today}.json"
            data = json.load(open(posts_path))
            for p in data.get("posts", [])[:5]:
                status = "✅" if p["under_limit"] else "⚠️"
                print(f"  {status} Post {p['index']}: {p['emoji']} {p['type']} ({p['char_count']} chars)")
        return 0
    
    if args.text:
        text = args.text
    else:
        post = load_todays_post(args.slot)
        if not post:
            return 1
        text = post["text"]
        print(f"📋 Selected Post {post['index']} ({post['type']}, {post['char_count']} chars)")
    
    if len(text) > 280:
        print(f"⚠️  Text is {len(text)} chars (over 280). Trim or verify thread support.")
    
    return 0 if post_to_x(text, dry_run=args.dry_run) else 1

if __name__ == "__main__":
    sys.exit(main())
