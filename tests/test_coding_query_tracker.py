#!/usr/bin/env python3
"""Tests for coding_query_tracker.py"""

import json
import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

# Import the module under test
import sys
sys.path.insert(0, '/data/.openclaw/workspace/scripts')
from coding_query_tracker import (
    is_coding_query, get_daily_summary, save_daily_report,
    get_historical_hit_rates, LOG_FILE, LOG_DIR, DAILY_REPORT_DIR
)

class TestIsCodingQuery:
    def test_simple_coding_terms(self):
        assert is_coding_query("How do I write a Python function?") is True
        assert is_coding_query("Debug this JavaScript error") is True
        assert is_coding_query("Deploy to AWS") is True
    
    def test_negative_cases(self):
        assert is_coding_query("What's the weather today?") is False
        assert is_coding_query("Tell me a joke") is False
        assert is_coding_query("Order pizza") is False
    
    def test_edge_cases(self):
        assert is_coding_query("") is False
        assert is_coding_query("code") is True  # Single keyword
        assert is_coding_query("CODE") is True  # Case insensitive

class TestDailySummary:
    def test_empty_log(self):
        # When LOG_FILE exists but has no entries for target date
        result = get_daily_summary(date(1900, 1, 1))
        assert result["coding_queries"] == 0
        assert result["non_coding_queries"] == 0
        assert result["total_queries"] == 0
        assert result["coding_hit_rate_percent"] == 0.0
        assert result["total_tokens_saved"] == 0
    
    def test_with_entries(self, tmp_path):
        # Create temporary log
        log_file = tmp_path / "test_queries.jsonl"
        entries = [
            {"date": "2026-05-04", "is_coding": True, "cache_hit": True, "tokens_saved": 100, "response_time_ms": 50.0},
            {"date": "2026-05-04", "is_coding": True, "cache_hit": False, "tokens_saved": 0, "response_time_ms": 100.0},
            {"date": "2026-05-04", "is_coding": False, "cache_hit": False, "tokens_saved": 0, "response_time_ms": 25.0},
        ]
        
        with open(log_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        # Monkeypatch LOG_FILE
        import coding_query_tracker
        original_log = coding_query_tracker.LOG_FILE
        coding_query_tracker.LOG_FILE = log_file
        
        try:
            result = get_daily_summary(date(2026, 5, 4))
            assert result["coding_queries"] == 2
            assert result["coding_cache_hits"] == 1
            assert result["coding_hit_rate_percent"] == 50.0
            assert result["non_coding_queries"] == 1
            assert result["total_queries"] == 3
            assert result["total_tokens_saved"] == 100
        finally:
            coding_query_tracker.LOG_FILE = original_log
    
    def test_zero_hit_rate(self, tmp_path):
        log_file = tmp_path / "test_queries.jsonl"
        entries = [
            {"date": "2026-05-04", "is_coding": True, "cache_hit": False, "tokens_saved": 0, "response_time_ms": 50.0},
        ]
        
        with open(log_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        import coding_query_tracker
        original_log = coding_query_tracker.LOG_FILE
        coding_query_tracker.LOG_FILE = log_file
        
        try:
            result = get_daily_summary(date(2026, 5, 4))
            assert result["coding_hit_rate_percent"] == 0.0
        finally:
            coding_query_tracker.LOG_FILE = original_log

class TestSaveDailyReport:
    def test_report_file_created(self, tmp_path):
        import coding_query_tracker
        
        # Create temp directories
        report_dir = tmp_path / "daily_reports"
        report_dir.mkdir()
        
        log_file = tmp_path / "queries.jsonl"
        entries = [
            {"date": "2026-05-04", "is_coding": True, "cache_hit": True, "tokens_saved": 50, "response_time_ms": 30.0},
        ]
        with open(log_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        # Monkeypatch
        original_log = coding_query_tracker.LOG_FILE
        original_report_dir = coding_query_tracker.DAILY_REPORT_DIR
        coding_query_tracker.LOG_FILE = log_file
        coding_query_tracker.DAILY_REPORT_DIR = report_dir
        
        try:
            result = save_daily_report(date(2026, 5, 4))
            assert result["date"] == "2026-05-04"
            
            report_file = report_dir / "coding_queries_2026-05-04.json"
            assert report_file.exists()
            
            with open(report_file) as f:
                saved = json.load(f)
            assert saved["coding_queries"] == 1
        finally:
            coding_query_tracker.LOG_FILE = original_log
            coding_query_tracker.DAILY_REPORT_DIR = original_report_dir

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
