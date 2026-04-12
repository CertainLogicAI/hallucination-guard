#!/usr/bin/env python3
"""
Token Reduction Engine - Stress Test
-------------------------------------
Runs 20,000 queries through the token reduction engine and generates a performance report.
"""

import json
import time
import sys
import os
import random
import hashlib
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_reduction_engine import reduce_tokens, get_metrics, clear_cache

TOTAL_QUERIES = 20000
BATCH_SIZE = 1000

test_queries = [
    # Short queries
    "How do I fix PLC communication errors",
    "What is IEC 61131-3",
    "Ladder logic tutorial",
    "Fix rung 42 timing issue",
    "PLC scan time optimization",
    # Medium queries
    "Write structured text for PID controller with anti-windup and manual mode",
    "How to implement Modbus TCP communication between two ControlLogix controllers",
    "Design a state machine for conveyor belt control with fault handling",
    "Explain the difference between function block diagram and ladder logic",
    "Best practices for organizing tag databases in Studio 5000",
    # Long queries
    "I need help debugging a complex ControlLogix system that has intermittent communication faults on the Ethernet/IP network. The fault occurs every 30 minutes and causes a major fault on the processor. I've checked all the cabling and the switches are industrial grade. The error code is 16#0002 on the ENBT module. What could be causing this and how do I troubleshoot it step by step",
    "Design a comprehensive safety interlock system using safe I/O modules on a CompactLogix controller. The system needs to monitor emergency stops, light curtains, safety mats, and two-hand controls across three different zones. Each zone has independent shutdown requirements but the master E-stop should shut down everything. Include proper reset sequences, feedback monitoring, and diagnostic messaging requirements",
    "Create a production tracking system that counts parts on a conveyor line using photoelectric sensors. The system should track good parts, bad parts, and total production per shift. Include OEE calculations, downtime tracking with reason codes, shift handover logging, and hourly production rate monitoring with alarms when rates fall below target thresholds",
    "Help me optimize a large PLC program that has grown to over 50,000 lines of ladder logic. The scan time has increased to 250ms and is causing issues with high-speed counting and motion control synchronization. What are the best strategies for reducing scan time including task prioritization, interrupt handling, code restructuring, and I/O update strategies for ControlLogix platform",
    # Repeated queries (cache testing)
    "How do I fix PLC communication errors",
    "What is IEC 61131-3",
    "Ladder logic tutorial",
    "How do I fix PLC communication errors",
    "What is IEC 61131-3",
    "Ladder logic tutorial",
    "How do I fix PLC communication errors",
    "What is IEC 61131-3",
    "Ladder logic tutorial",
    "How do I fix PLC communication errors",
    # Very long queries
    "I'm working on a batch processing application that requires precise control of multiple heating zones, pressure vessels, and agitation motors. The process involves 15 distinct phases with specific temperature ramps, hold periods, pressure targets, and agitation speeds. Each phase has quality checkpoints where the operator must verify parameters before proceeding. I need help designing the state machine architecture, recipe management system, operator interface requirements, alarm handling for out-of-spec conditions, data logging for FDA 21 CFR Part 11 compliance, and integration with the plant MES system via OPC UA. The controller is a ControlLogix L85E with three EN2T modules. Currently using FactoryTalk View ME for the HMI. What's the best approach to structure this for scalability and maintainability",
    "Need to implement a motion control application with four servos coordinated through a multi-axis group. The application requires electronic camming, electronic gearing, and registration moves. The master encoder is a linear encoder on the primary axis with 20000 counts per inch resolution. Slave axes need to synchronize within 0.001 inch tolerance. I need help with the motion group configuration, cam table generation, registration sensor setup, following error monitoring, and tuning parameters to minimize tracking error during acceleration and deceleration profiles. Also need advice on the electrical design including brake controls and safe torque off implementation",
    "We're having issues with a FactoryTalk View ME application that randomly loses communication with the PanelView Plus 1000 terminal running runtime version 12. The application was migrated from version 9 and uses factory acceptance tested code. Communication drops happen roughly every 2-3 hours and require a cold restart of the terminal. We've tried increasing timeouts, disabling screen transitions, and updating firmware. The terminal communicates with three PLCs via different subnets. Need troubleshooting steps for the communication drivers, display resolution settings, memory management on the terminal, and potential issues with the migration process from version 9 to 12",
]

print(f"🚀 Token Reduction Engine Stress Test")
print(f"{'='*50}")
print(f"Total queries: {TOTAL_QUERIES}")
print(f"Unique test queries: {len(test_queries)}")
print(f"Starting...\n")

clear_cache()
start_time = time.time()
errors = 0
results_by_method = defaultdict(int)
tokens_saved_total = 0
original_tokens_total = 0
reduced_tokens_total = 0
cache_hits = 0

for i in range(1, TOTAL_QUERIES + 1):
    query = test_queries[i % len(test_queries)]
    try:
        result = reduce_tokens(query)
        results_by_method[result['method']] += 1
        tokens_saved_total += result['tokens_saved']
        original_tokens_total += result['original_tokens']
        reduced_tokens_total += result['reduced_tokens']
        if result['cache_hit']:
            cache_hits += 1
    except Exception as e:
        errors += 1

    if i % BATCH_SIZE == 0:
        elapsed = time.time() - start_time
        rate = i / elapsed
        metrics = get_metrics()
        print(f"  [{i:>6}/{TOTAL_QUERIES}] "
              f"Rate: {rate:,.0f} q/s | "
              f"Cache: {metrics['cache_hit_rate_percent']:.1f}% | "
              f"Avg saved: {metrics['average_tokens_saved_per_query']:.1f} | "
              f"Errors: {errors}")

total_time = time.time() - start_time
final_metrics = get_metrics()

print(f"\n{'='*50}")
print(f"📊 STRESS TEST RESULTS")
print(f"{'='*50}")
print(f"Total queries:     {TOTAL_QUERIES:,}")
print(f"Total time:        {total_time:.2f}s")
print(f"Throughput:        {TOTAL_QUERIES/total_time:,.0f} queries/sec")
print(f"Errors:            {errors}")
print(f"")
print(f"📈 CACHE PERFORMANCE")
print(f"Cache hits:        {cache_hits:,} ({final_metrics['cache_hit_rate_percent']:.1f}%)")
print(f"Cache misses:      {TOTAL_QUERIES - cache_hits:,}")
print(f"Final cache size:  {len(list(final_metrics.keys()))}")
print(f"")
print(f"💰 TOKEN SAVINGS")
print(f"Original tokens:   {original_tokens_total:,}")
print(f"Reduced tokens:    {reduced_tokens_total:,}")
print(f"Tokens saved:      {tokens_saved_total:,}")
if original_tokens_total > 0:
    print(f"Reduction rate:    {(tokens_saved_total/original_tokens_total)*100:.1f}%")
print(f"Avg saved/query:   {tokens_saved_total/TOTAL_QUERIES:.1f}")
print(f"")
print(f"🔧 METHODS USED")
for method, count in sorted(results_by_method.items()):
    print(f"  {method:<15}: {count:>6,} ({count/TOTAL_QUERIES*100:.1f}%)")
print(f"{'='*50}")

report = {
    'total_queries': TOTAL_QUIES,
    'total_time_seconds': round(total_time, 2),
    'throughput_qps': round(TOTAL_QUERIES / total_time, 2),
    'errors': errors,
    'cache_hit_rate': round(final_metrics['cache_hit_rate_percent'], 2),
    'tokens_saved': tokens_saved_total,
    'reduction_rate_percent': round((tokens_saved_total / original_tokens_total) * 100, 2) if original_tokens_total > 0 else 0,
    'methods': dict(results_by_method)
}

with open('/data/.openclaw/workspace/token_stress_test_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print(f"\nReport saved to token_stress_test_report.json")
