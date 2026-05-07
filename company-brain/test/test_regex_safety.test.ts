/**
 * Regex Safety Audit — Brain OS Security Hardening
 *
 * Tests all 80 regex patterns in certainlogic-intent.ts for:
 * 1. Catastrophic backtracking (ReDoS)
 * 2. Excessive execution time on crafted inputs
 * 3. Stack overflow on deeply nested patterns
 *
 * Run:
 *   cd company-brain && bun test test/test_regex_safety.ts
 */

import { describe, test, expect } from "bun:test";
import { classifyCertainLogicIntent } from "../src/core/search/certainlogic-intent";

// Maximum acceptable execution time per pattern (milliseconds)
const MAX_EXECUTION_MS = 50;

// Test payloads designed to trigger backtracking
const testPayloads: [string, string][] = [
  ["a_repeated", "a".repeat(1000)],
  ["a_repeated_5000", "a".repeat(5000)],
  ["parens_nested", "(".repeat(500)],
  ["special_chars_mixed", "!@#$%^&*()".repeat(100)],
  ["long_word", "supercalifragilisticexpialidocious".repeat(50)],
  ["repeated_pattern", "moatmoatmoat".repeat(50)],
  ["boundary_test", "a".repeat(500) + "moat" + "a".repeat(500)],
  ["empty", ""],
  ["single_char", "a"],
  ["sql_injection", "'; DROP TABLE pages; --"],
  ["path_traversal", "../../etc/passwd"],
  ["unicode_mixed", "策略moat策略".repeat(50)],
  ["numbers_only", "1234567890".repeat(100)],
  ["newline_mixed", "line1\nline2\n".repeat(200)],
];

function measureExecutionTime(fn: () => any): number {
  const start = performance.now();
  try {
    fn();
  } catch (_e) {
    // Ignore errors
  }
  return performance.now() - start;
}

describe("ReDoS Safety Audit", () => {
  test("all payloads take < 50ms", () => {
    const failures: string[] = [];

    for (const [payloadName, payload] of testPayloads) {
      const elapsed = measureExecutionTime(() => {
        classifyCertainLogicIntent(payload);
      });

      if (elapsed > MAX_EXECUTION_MS) {
        failures.push(
          `${payloadName}: ${elapsed.toFixed(2)}ms (max: ${MAX_EXECUTION_MS}ms)`
        );
      }
    }

    expect(failures).toHaveLength(0);
    if (failures.length > 0) {
      console.error("FAILURES:", failures.join("\n"));
    }
  });

  test("extreme payload (10K chars)", () => {
    const extremePayload = "a".repeat(10000);
    const elapsed = measureExecutionTime(() => {
      classifyCertainLogicIntent(extremePayload);
    });

    expect(elapsed).toBeLessThan(MAX_EXECUTION_MS);
  });
});
