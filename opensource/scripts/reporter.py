#!/usr/bin/env python3
"""
scripts/reporter.py — Human-readable reporting for Telegram / Discord.

Architecture decisions:
- Pure formatting module: no side effects, no network calls.
- Emoji-based status indicators for quick visual parsing in mobile notifications.
- All floating-point accuracy values are formatted as percentages with 1 decimal.
- Escalation alerts include the raw details dict for programmatic downstream handling.
"""


def _pct(val: float) -> str:
    """Format a float as a percentage string with 1 decimal place."""
    return f"{val * 100:.1f}%"


def _delta(before: float, after: float) -> str:
    """Return a signed delta percentage string."""
    d = after - before
    sign = "+" if d >= 0 else ""
    return f"{sign}{d * 100:.1f}%"


def format_iteration_summary(
    iteration: int,
    accuracy_before: float,
    accuracy_after: float,
    fixes_applied: int,
    subagent_spawns: int,
    cost_total: float,
    commit_hash: str,
    all_passed: bool,
    cases_improved: int = 0,
    cases_total: int = 0,
) -> str:
    """
    Return a Telegram/Discord formatted message for a completed iteration.
    """
    delta_str = _delta(accuracy_before, accuracy_after)
    status_emoji = "✅" if all_passed else "🚨 REGRESSION — reverted"
    commit_short = commit_hash[:8] if len(commit_hash) >= 8 else commit_hash

    lines = [
        f"🔄 Iteration {iteration} Complete",
        f"",
        f"Accuracy: {_pct(accuracy_before)} → {_pct(accuracy_after)} ({delta_str})",
        f"Cases improved: +{cases_improved}/{cases_total}",
        f"Fixes applied: {fixes_applied} auto, {subagent_spawns} subagent",
        f"",
        f"Verification: {status_emoji}",
        f"Cost: ${cost_total:.4f}",
        f"Commit: `{commit_short}`",
    ]
    return "\n".join(lines)


def format_daily_report(
    iterations: list[dict],
    total_spend: float,
    accuracy_trend: list[float],
    target_accuracy: float = 0.95,
) -> str:
    """
    Return a daily summary report.

    Args:
        iterations: List of iteration result dicts (each should have 'fixes_applied',
                    'subagent_spawns', etc.)
        total_spend: Total USD spent today.
        accuracy_trend: List of accuracy values in chronological order.
        target_accuracy: Target accuracy to report progress against.
    """
    auto_fixes = sum(i.get("fixes_applied", 0) for i in iterations)
    subagents = sum(i.get("subagent_spawns", 0) for i in iterations)

    start_acc = accuracy_trend[0] if accuracy_trend else 0.0
    end_acc = accuracy_trend[-1] if accuracy_trend else 0.0

    if end_acc >= target_accuracy:
        status = f"✅ Target {target_accuracy:.0%} reached"
    else:
        remaining = target_accuracy - end_acc
        status = f"📈 {remaining * 100:.1f}pp to target {target_accuracy:.0%}"

    lines = [
        f"📊 Daily Cost Report",
        f"",
        f"Iterations run: {len(iterations)}",
        f"Total spend: ${total_spend:.4f}",
        f"Auto-fixes: {auto_fixes}",
        f"Subagents: {subagents}",
        f"Accuracy trend: {_pct(start_acc)} → {_pct(end_acc)}",
        f"Status: {status}",
    ]
    return "\n".join(lines)


def format_escalation_alert(reason: str, details: dict, action: str = "") -> str:
    """
    Return an immediate escalation alert for human review.

    Args:
        reason: Short human-readable reason (e.g., "3 consecutive regressions").
        details: Dict of structured details for debugging.
        action: Human-actionable instruction.
    """
    lines = [
        f"🚨 ESCALATION: {reason}",
        f"",
    ]
    # Include top-level detail keys in a readable bulleted format
    for key, value in sorted(details.items()):
        lines.append(f"• {key}: {value}")
    if action:
        lines.append(f"")
        lines.append(f"Action required: {action}")
    return "\n".join(lines)
