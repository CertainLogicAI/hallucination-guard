"""
Fallback Logging System for Deterministic AI Brain
Tracks external LLM usage, costs, and optimization opportunities
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict
import threading

class FallbackLogger:
    def __init__(self, log_file: str = "/data/.openclaw/workspace/fallback_logs.json"):
        self.log_file = log_file
        self.lock = threading.Lock()
        self.stats = defaultdict(int)
        self.costs = defaultdict(float)
        self._load_logs()
        
    def _load_logs(self):
        """Load existing logs from file"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                self.stats = defaultdict(int, data.get('stats', {}))
                self.costs = defaultdict(float, data.get('costs', {}))
        except FileNotFoundError:
            pass
            
    def _save_logs(self):
        """Save logs to file"""
        with self.lock:
            with open(self.log_file, 'w') as f:
                json.dump({
                    'stats': dict(self.stats),
                    'costs': dict(self.costs),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
                
    def log_fallback_call(self, 
                         query: str, 
                         model_used: str, 
                         input_tokens: int, 
                         output_tokens: int,
                         cost_per_1k_tokens: float = 0.002):
        """Log an external LLM fallback call"""
        with self.lock:
            # Update stats
            self.stats['total_fallbacks'] += 1
            self.stats[f'fallbacks_{model_used}'] += 1
            self.stats['total_input_tokens'] += input_tokens
            self.stats['total_output_tokens'] += output_tokens
            
            # Calculate cost
            cost = (input_tokens + output_tokens) / 1000 * cost_per_1k_tokens
            self.stats['total_cost'] += cost
            self.costs[model_used] += cost
            
            # Log detailed call
            call_log = {
                'timestamp': datetime.now().isoformat(),
                'query': query[:100],  # Truncate for privacy
                'model_used': model_used,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': cost,
                'query_hash': hash(query)  # For deduplication without storing full query
            }
            
            # Append to detailed log (optional - can be disabled for privacy)
            try:
                with open("/data/.openclaw/workspace/fallback_detailed.log", 'a') as f:
                    f.write(json.dumps(call_log) + '\n')
            except:
                pass  # Fail silently if detailed logging not needed
                
            self._save_logs()
            
    def get_fallback_rate(self, total_queries: int) -> float:
        """Calculate fallback rate as percentage"""
        if total_queries == 0:
            return 0.0
        return (self.stats['total_fallbacks'] / total_queries) * 100
        
    def get_average_cost_per_query(self) -> float:
        """Calculate average cost per fallback query"""
        if self.stats['total_fallbacks'] == 0:
            return 0.0
        return self.stats['total_cost'] / self.stats['total_fallbacks']
        
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        with self.lock:
            return {
                'total_fallbacks': self.stats['total_fallbacks'],
                'fallbacks_by_model': {k: v for k, v in self.stats.items() if k.startswith('fallbacks_')},
                'total_input_tokens': self.stats['total_input_tokens'],
                'total_output_tokens': self.stats['total_output_tokens'],
                'total_cost': round(self.stats['total_cost'], 4),
                'average_cost_per_query': round(self.get_average_cost_per_query(), 4),
                'last_updated': datetime.now().isoformat()
            }
            
    def check_optimization_thresholds(self, 
                                    fallback_rate_threshold: float = 15.0,
                                    cost_threshold: float = 10.0) -> list:
        """Check if optimization is needed based on thresholds"""
        alerts = []
        
        # This would need total_queries from main app - placeholder
        # In practice, you'd pass total_queries from your metrics
        
        if self.stats['total_cost'] > cost_threshold:
            alerts.append({
                'type': 'cost_threshold',
                'message': f'Fallback costs exceed ${cost_threshold}: ${self.stats["total_cost"]:.2f}',
                'severity': 'warning'
            })
            
        return alerts

# Global logger instance
fallback_logger = FallbackLogger()

def log_fallback(query: str, model: str, input_tokens: int, output_tokens: int):
    """Convenience function for logging fallbacks"""
    fallback_logger.log_fallback_call(query, model, input_tokens, output_tokens)

def get_fallback_stats() -> dict:
    """Get current fallback statistics"""
    return fallback_logger.get_stats()