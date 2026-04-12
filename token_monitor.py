#!/usr/bin/env python3
"""
Real-time Token Savings Monitor for Deterministic AI Layer
---------------------------------------------------------
Monitors token reduction engine performance, generates alerts, and produces reports.
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
METRICS_FILE = "/data/.openclaw/workspace/token_metrics.json"
ALERT_THRESHOLD_CACHE_HIT = 95.0  # Alert if cache hit rate drops below this %
ALERT_THRESHOLD_SAVINGS = 400  # Alert if avg tokens saved drops below this
REPORT_INTERVAL = 60  # Seconds between checks
LOG_FILE = "/data/.openclaw/workspace/token_monitor.log"

class TokenMonitor:
    def __init__(self, metrics_file: str = METRICS_FILE):
        self.metrics_file = Path(metrics_file)
        self.metrics_history: List[Dict] = []
        self.alerts_sent = set()
        self.cost_per_million_tokens = 15.0  # Claude Opus rate $/1M tokens

    def load_metrics(self) -> Optional[Dict]:
        """Load latest metrics from file."""
        if not self.metrics_file.exists():
            return None
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data[-1]  # Get latest entry
            return data
        except (json.JSONDecodeError, IndexError) as e:
            self.log(f"Error reading metrics: {e}")
            return None

    def calculate_cost_savings(self, metrics: Dict) -> Dict:
        """Calculate cost savings based on token reduction."""
        original_tokens = metrics.get('original_tokens_total', 0)
        reduced_tokens = metrics.get('reduced_tokens_total', 0)
        tokens_saved = original_tokens - reduced_tokens
        cost_without = (original_tokens / 1_000_000) * self.cost_per_million_tokens
        cost_with = (reduced_tokens / 1_000_000) * self.cost_per_million_tokens
        savings = cost_without - cost_with
        savings_percent = (savings / cost_without * 100) if cost_without > 0 else 0

        return {
            'tokens_saved': tokens_saved,
            'cost_without_engine_usd': round(cost_without, 4),
            'cost_with_engine_usd': round(cost_with, 4),
            'savings_usd': round(savings, 4),
            'savings_percent': round(savings_percent, 2)
        }

    def check_alerts(self, metrics: Dict):
        """Check if any thresholds are breached and send alerts."""
        cache_hit_rate = metrics.get('cache_hit_rate_percent', 0)
        avg_saved = metrics.get('average_tokens_saved_per_query', 0)

        alerts = []

        if cache_hit_rate < ALERT_THRESHOLD_CACHE_HIT:
            alerts.append(f"Low cache hit rate: {cache_hit_rate:.1f}% (threshold: {ALERT_THRESHACHE_HIT}%)")

        if avg_saved < ALERT_THRESHOLD_SAVINGS:
            alerts.append(f"Low token savings: {avg_saved:.1f} tokens/query (threshold: {ALERT_THRESHOLD_SAVINGS})")

        # Send alerts if any triggered and not sent recently
        for alert in alerts:
            alert_key = f"{metrics.get('timestamp', '')}:{alert}"
            if alert_key not in self.alerts_sent:
                self.send_alert(alert, metrics)
                self.alerts_sent.add(alert_key)

    def send_alert(self, message: str, metrics: Dict):
        """Send alert via console log (expand to email/Slack as needed)."""
        log_msg = f"[ALERT] {datetime.now().isoformat()} - {message}\nMetrics: {json.dumps(metrics, indent=2)}"
        self.log(log_msg)
        # TODO: Add email/Slack integration here if needed
        print(f"🚨 ALERT: {message}")

    def generate_daily_report(self) -> Dict:
        """Generate a daily summary report from history."""
        if not self.metrics_history:
            return {}

        # Group by day
        daily = {}
        for entry in self.metrics_history:
            date = entry.get('timestamp', '').split('T')[0]
            daily.setdefault(date, []).append(entry)

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_days': len(daily),
            'daily_summaries': {}
        }

        for date, entries in daily.items():
            avg_cache_hit = sum(e.get('cache_hit_rate_percent', 0) for e in entries) / len(entries)
            total_queries = sum(e.get('total_queries', 0) for e in entries)
            total_saved = sum(e.get('total_tokens_saved', 0) for e in entries)

            report['daily_summaries'][date] = {
                'avg_cache_hit_rate': round(avg_cache_hit, 2),
                'total_queries': total_queries,
                'total_tokens_saved': total_saved,
                'estimated_daily_savings_usd': round((total_saved / 1_000_000) * self.cost_per_million_tokens, 2)
            }

        return report

    def log(self, message: str):
        """Write log entry to file."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)

    def run(self, max_iterations: Optional[int] = None, generate_report_at_end: bool = False):
        """Main monitoring loop."""
        self.log("Token monitor started")
        iterations = 0

        try:
            while True:
                metrics = self.load_metrics()
                if metrics:
                    self.metrics_history.append(metrics)
                    self.check_alerts(metrics)

                    # Print status to console
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Cache hit: {metrics.get('cache_hit_rate_percent'):.1f}% | "
                          f"Saved/query: {metrics.get('average_tokens_saved_per_query'):.0f} tokens | "
                          f"Total saved: {metrics.get('total_tokens_saved'):,}", end='', flush=True)

                time.sleep(REPORT_INTERVAL)
                iterations += 1

                if max_iterations and iterations >= max_iterations:
                    break

        except KeyboardInterrupt:
            self.log("Token monitor stopped by user")
            print("\nMonitor stopped.")

        if generate_report_at_end and self.metrics_history:
            report = self.generate_daily_report()
            report_file = f"/data/.openclaw/workspace/token_monitor_report_{datetime.now().strftime('%Y-%m-%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.log(f"Daily report generated: {report_file}")
            print(f"\n📊 Report saved to: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Token Reduction Engine Monitor")
    parser.add_argument("--interval", type=int, default=REPORT_INTERVAL,
                        help="Check interval in seconds (default: 60)")
    parser.add_argument("--iterations", type=int, default=None,
                        help="Number of iterations to run (default: infinite)")
    parser.add_argument("--report", action="store_true",
                        help="Generate daily report at exit")
    parser.add_argument("--metrics-file", default=METRICS_FILE,
                        help=f"Path to metrics file (default: {METRICS_FILE})")

    args = parser.parse_args()

    monitor = TokenMonitor(metrics_file=args.metrics_file)
    monitor.run(max_iterations=args.iterations, generate_report_at_end=args.report)

if __name__ == "__main__":
    main()