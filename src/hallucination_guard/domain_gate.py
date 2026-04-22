"""
CertainLogic Domain Gate + Hit Rate Tracker

Prevents out-of-scope facts from hitting the Brain API.
Tracks validation success rates by domain.
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class DomainResult:
    query: str
    domain: str
    action: str  # 'validate', 'skip', 'unclear'
    confidence: float
    timestamp: float


@dataclass  
class HitRateStats:
    total_queries: int = 0
    in_scope: int = 0
    out_scope: int = 0
    unclear: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    api_calls_saved: int = 0
    by_domain: Dict[str, int] = None
    
    def __post_init__(self):
        if self.by_domain is None:
            self.by_domain = {}


class DomainGate:
    """Classifies facts into domains and decides whether to validate."""
    
    # In-scope: Technical/coding domains we have facts for
    IN_SCOPE_PATTERNS = [
        (r'\b(python|javascript|typescript|js|ts|node|npm)\b', 'languages'),
        (r'\b(http|https|api|rest|json|xml|graphql|grpc)\b', 'apis'),
        (r'\b(git|github|gitlab|commit|branch|merge|rebase)\b', 'git'),
        (r'\b(docker|container|kubernetes|k8s|pod|helm)\b', 'containers'),
        (r'\b(sql|database|postgres|mysql|mongodb|redis)\b', 'databases'),
        (r'\b(jwt|oauth|csrf|xss|cript|hash|encrypt|tls|ssl)\b', 'security'),
        (r'\b(fastapi|flask|django|react|vue|angular|next\.js)\b', 'frameworks'),
        (r'\b(aws|gcp|azure|cloud|lambda|s3|ec2)\b', 'cloud'),
        (r'\b(test|pytest|unittest|mock|fixture|coverage)\b', 'testing'),
        (r'\b(linux|unix|bash|shell|terminal|command)\b', 'systems'),
        (r'\b(status\s*\d{3}|http\s*\d{3}|error\s*\d{3})\b', 'status_codes'),
        (r'\b(version|release|eol|deprecated|stable|beta|alpha)\b', 'versions'),
    ]
    
    # Out-of-scope: Personal, business, current events we explicitly skip
    OUT_SCOPE_PATTERNS = [
        (r'\b(birthday|born|age|wife|husband|daughter|son|family)\b', 'personal'),
        (r'\b(revenue|profit|earnings|stock\s+price|market\s+cap)\b', 'financial'),
        (r'\b(i\s+(was|am|did|have|think|believe|feel))\b', 'subjective'),
        (r'\b(yesterday|today|tomorrow|last\s+week|next\s+month)\b', 'current_events'),
        (r'\b(restaurant|hotel|vacation|trip|travel|flight)\b', 'lifestyle'),
        (r'\b(opinion|think|believe|feel|prefer|like|dislike)\b', 'opinion'),
        (r'\b(weather|forecast|temperature|rain|snow)\b', 'weather'),
    ]
    
    def classify(self, query: str) -> Tuple[str, str, float]:
        """
        Classify a query and decide action.
        
        Returns: (domain, action, confidence)
        - domain: 'languages', 'apis', 'personal', 'financial', etc.
        - action: 'validate' (in-scope), 'skip' (out-of-scope), 'unclear'
        - confidence: 0.0-1.0
        """
        query_lower = query.lower()
        
        # Check out-of-scope first (stronger signal)
        for pattern, domain in self.OUT_SCOPE_PATTERNS:
            if re.search(pattern, query_lower):
                return domain, 'skip', 0.9
        
        # Check in-scope
        for pattern, domain in self.IN_SCOPE_PATTERNS:
            if re.search(pattern, query_lower):
                return domain, 'validate', 0.85
        
        # Unclear - let it through to be safe
        return 'unclear', 'validate', 0.5
    
    def should_validate(self, query: str) -> bool:
        """Quick check: should we validate this fact?"""
        _, action, _ = self.classify(query)
        return action == 'validate'


class HitRateTracker:
    """Tracks validation hit rates and saves metrics."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / '.hallucination-guard'
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / 'hit_rate_metrics.json'
        self.results_file = self.data_dir / 'domain_results.jsonl'
        
        self.stats = self._load_stats()
        self.gate = DomainGate()
    
    def _load_stats(self) -> HitRateStats:
        """Load persisted stats."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file) as f:
                    data = json.load(f)
                return HitRateStats(**data)
            except Exception:
                pass
        return HitRateStats()
    
    def _save_stats(self):
        """Persist stats."""
        with open(self.metrics_file, 'w') as f:
            json.dump(asdict(self.stats), f, indent=2)
    
    def track_query(self, query: str, cache_hit: bool = None) -> DomainResult:
        """
        Track a query through the domain gate.
        
        Args:
            query: The fact/query being checked
            cache_hit: True if answered from cache, False if API needed, None if skipped
        """
        domain, action, confidence = self.gate.classify(query)
        
        # Update stats
        self.stats.total_queries += 1
        
        if action == 'validate':
            self.stats.in_scope += 1
            if cache_hit is True:
                self.stats.cache_hits += 1
            elif cache_hit is False:
                self.stats.cache_misses += 1
        elif action == 'skip':
            self.stats.out_scope += 1
            self.stats.api_calls_saved += 1
        else:  # unclear
            self.stats.unclear += 1
        
        # Track by domain
        self.stats.by_domain[domain] = self.stats.by_domain.get(domain, 0) + 1
        
        # Save result
        result = DomainResult(
            query=query[:200],  # Truncate long queries
            domain=domain,
            action=action,
            confidence=confidence,
            timestamp=time.time()
        )
        
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')
        
        self._save_stats()
        return result
    
    def get_report(self) -> dict:
        """Generate a summary report."""
        total = self.stats.total_queries
        if total == 0:
            return {"status": "no_data", "message": "No queries tracked yet"}
        
        in_scope_pct = (self.stats.in_scope / total) * 100
        out_scope_pct = (self.stats.out_scope / total) * 100
        unclear_pct = (self.stats.unclear / total) * 100
        
        cache_total = self.stats.cache_hits + self.stats.cache_misses
        cache_rate = (self.stats.cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            "status": "ok",
            "total_queries": total,
            "in_scope": {
                "count": self.stats.in_scope,
                "percentage": round(in_scope_pct, 1),
                "cache_hits": self.stats.cache_hits,
                "cache_misses": self.stats.cache_misses,
                "cache_hit_rate": round(cache_rate, 1),
            },
            "out_scope": {
                "count": self.stats.out_scope,
                "percentage": round(out_scope_pct, 1),
                "api_calls_saved": self.stats.api_calls_saved,
            },
            "unclear": {
                "count": self.stats.unclear,
                "percentage": round(unclear_pct, 1),
            },
            "by_domain": self.stats.by_domain,
        }
    
    def print_report(self):
        """Print a human-readable report."""
        report = self.get_report()
        
        if report["status"] == "no_data":
            print(report["message"])
            return
        
        print("=" * 50)
        print("CERTAINLOGIC DOMAIN GATE — HIT RATE REPORT")
        print("=" * 50)
        print()
        print(f"Total Queries:     {report['total_queries']}")
        print()
        print("SCOPE BREAKDOWN:")
        print(f"  In-Scope:        {report['in_scope']['count']} ({report['in_scope']['percentage']}%)")
        print(f"    Cache Hits:    {report['in_scope']['cache_hits']}")
        print(f"    Cache Misses:  {report['in_scope']['cache_misses']}")
        print(f"    Hit Rate:      {report['in_scope']['cache_hit_rate']}%")
        print(f"  Out-of-Scope:    {report['out_scope']['count']} ({report['out_scope']['percentage']}%)")
        print(f"    API Calls Saved: {report['out_scope']['api_calls_saved']}")
        print(f"  Unclear:         {report['unclear']['count']} ({report['unclear']['percentage']}%)")
        print()
        print("BY DOMAIN:")
        for domain, count in sorted(report['by_domain'].items(), key=lambda x: -x[1]):
            print(f"  {domain:20s} {count:5d}")
        print()
        print("=" * 50)


# CLI interface
if __name__ == "__main__":
    import sys
    
    tracker = HitRateTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        tracker.print_report()
    else:
        # Demo/test mode
        test_queries = [
            "Python list is mutable",
            "HTTP status 429 means rate limited",
            "Git rebase vs merge",
            "Sarah's birthday is March 15",
            "Acme Corp revenue 2026",
            "I think React is better than Vue",
            "Docker compose up",
            "JWT structure",
            "Weather in London today",
            "FastAPI automatic docs URL",
        ]
        
        print("Testing domain gate with sample queries:\n")
        for query in test_queries:
            result = tracker.track_query(query, cache_hit=True)
            action_icon = "✅" if result.action == 'validate' else "🚫" if result.action == 'skip' else "❓"
            print(f"{action_icon} [{result.domain:15s}] {result.action:10s} | {query}")
        
        print()
        tracker.print_report()
