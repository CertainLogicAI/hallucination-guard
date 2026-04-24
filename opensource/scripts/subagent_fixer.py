#!/usr/bin/env python3
"""
scripts/subagent_fixer.py — Subagent spawn, patch extraction, and verification.

Spawn mechanism chosen: **subprocess + OpenClaw agent CLI**
Rationale: subprocess is portable, testable in dry-run mode.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_TIMEOUT = 300  # seconds
DEFAULT_MODEL = "openrouter/moonshotai/kimi-k2.6"


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def spawn_fix_subagent(proposal: dict, work_dir: Path | str, dry_run: bool = False) -> dict:
    if dry_run:
        task_dir = Path(work_dir) / "subagent_tasks" / f"{_now_str()}_dry_run"
        task_dir.mkdir(parents=True, exist_ok=True)
        _simulate_subagent(task_dir, proposal)
        return _gather_result(task_dir)

    pattern = proposal.get("pattern", "unknown")
    case_id = proposal.get("case_id", f"subagent-{_now_str()}")
    task_dir = Path(work_dir) / "subagent_tasks" / f"{_now_str()}_{pattern}"
    task_dir.mkdir(parents=True, exist_ok=True)

    query = proposal.get("query", "")
    expected = proposal.get("expected", "")
    actual = proposal.get("actual", "")
    target_file = proposal.get("target_file", "")

    task_md = f"""# Fix Task — {case_id}

- **Query:** {query}
- **Expected:** {expected}
- **Actual:** {actual}
- **Pattern:** {pattern}
- **Target File:** {target_file}
"""
    (task_dir / "TASK.md").write_text(task_md)

    target_path = Path(work_dir) / target_file if target_file else None
    ctx_parts = ["# Context\n"]
    if target_path and target_path.exists():
        ctx_parts.append(f"## {target_file}\n```python\n")
        ctx_parts.append(target_path.read_text())
        ctx_parts.append("\n```\n")

    test_dir = Path(work_dir) / "tests"
    if test_dir.exists():
        for tf in sorted(test_dir.glob("test_*.py")):
            ctx_parts.append(f"## tests/{tf.name}\n```python\n")
            ctx_parts.append(tf.read_text())
            ctx_parts.append("\n```\n")

    (task_dir / "CONTEXT.md").write_text("".join(ctx_parts))

    prompt = f"""Fix benchmark failure in hallucination-guard:

Query: {query}
Expected: {expected}
Actual: {actual}
Target file: {target_file}
Constraints: Only modify target file. Preserve tests. Add # [AUTO-FIX] {case_id}. Run pytest after change.
"""
    prompt_path = task_dir / "PROMPT.md"
    prompt_path.write_text(prompt)

    cmd = [
        "openclaw", "agent",
        "--input", str(prompt_path),
        "--output", str(task_dir / "RESULT.json"),
    ]

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(work_dir), env={**os.environ, "OPENCLAW_AGENT_MODEL": DEFAULT_MODEL},
        )
    except FileNotFoundError:
        _simulate_subagent(task_dir, proposal)
        return _gather_result(task_dir)

    try:
        stdout, stderr = proc.communicate(timeout=DEFAULT_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"status": "timeout", "patch": "", "explanation": f"Timed out after {DEFAULT_TIMEOUT}s", "cost_usd": 0.0, "task_dir": str(task_dir)}

    if proc.returncode != 0:
        return {"status": "failed", "patch": "", "explanation": stderr.decode()[:500], "cost_usd": 0.0, "task_dir": str(task_dir)}

    return _gather_result(task_dir)


def _simulate_subagent(task_dir: Path, proposal: dict) -> None:
    (task_dir / "RESULT.json").write_text(json.dumps({
        "status": "simulated",
        "explanation": "openclaw CLI not available; simulated dry-run result",
        "cost_usd": 0.0,
    }))


def _gather_result(task_dir: Path) -> dict:
    rp = task_dir / "RESULT.json"
    result = json.loads(rp.read_text()) if rp.exists() else {}
    patch = extract_patch_from_subagent_result(task_dir)
    return {
        "status": result.get("status") or ("success" if patch else "failed"),
        "patch": patch or "",
        "explanation": result.get("explanation", ""),
        "cost_usd": result.get("cost_usd", 0.0),
        "task_dir": str(task_dir),
    }


def extract_patch_from_subagent_result(result_dir: Path) -> Optional[str]:
    for name in ("PATCH.diff", "changes.diff", "patch.diff"):
        p = result_dir / name
        if p.exists():
            text = p.read_text()
            if _is_valid_unified_diff(text):
                return text

    for orig in result_dir.rglob("*.orig"):
        current = orig.with_suffix("")
        if current.exists():
            diff = _compute_diff(orig.read_text(), current.read_text(), str(current.name))
            if diff:
                return diff

    rp = result_dir / "RESULT.json"
    if rp.exists():
        data = json.loads(rp.read_text())
        patch_text = data.get("patch", "")
        if patch_text and _is_valid_unified_diff(patch_text):
            return patch_text

    return None


def _is_valid_unified_diff(text: str) -> bool:
    return "---" in text and "+++" in text and "@@" in text


def _compute_diff(old_text: str, new_text: str, filename: str) -> str:
    import difflib
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    if old_lines and not old_lines[-1].endswith("\n"):
        old_lines[-1] += "\n"
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}"))
    return "".join(diff)


def apply_subagent_patch(patch: str, target_file: Path, backup_dir: Path) -> bool:
    backup_dir.mkdir(parents=True, exist_ok=True)
    if not target_file.exists():
        return False
    backup = backup_dir / f"{target_file.name}.{int(time.time())}.bak"
    shutil.copy2(target_file, backup)
    try:
        _apply_unified_diff(patch, target_file)
        return True
    except Exception:
        try:
            proc = subprocess.run(["patch", "-p0", str(target_file)], input=patch, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        shutil.copy2(backup, target_file)
        return False


def _apply_unified_diff(diff_text: str, target_file: Path) -> None:
    lines = target_file.read_text().splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    diff_lines = diff_text.splitlines(keepends=True)
    if diff_lines and not diff_lines[-1].endswith("\n"):
        diff_lines[-1] += "\n"

    hunks = []
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        if line.startswith("@@"):
            m = re.match(r"@@ -(\d+)(?:(\d+))? \+(\d+)(?:(\d+))? @@", line)
            if m:
                old_start = int(m.group(1))
                old_count = int(m.group(2)) if m.group(2) else 1
                new_start = int(m.group(3))
                new_count = int(m.group(4)) if m.group(4) else 1
                hunk_lines = []
                i += 1
                while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
                    hunk_lines.append(diff_lines[i])
                    i += 1
                hunks.append({"old_start": old_start, "old_count": old_count, "new_start": new_start, "new_count": new_count, "lines": hunk_lines})
                continue
        i += 1

    if not hunks:
        raise ValueError("No valid hunks found")

    result = list(lines)
    for hunk in reversed(hunks):
        start = hunk["old_start"] - 1
        old_end = start + hunk["old_count"]
        new_lines = []
        for hl in hunk["lines"]:
            if hl.startswith("-"):
                pass
            elif hl.startswith("+"):
                new_lines.append(hl[1:])
            elif hl.startswith(" "):
                new_lines.append(hl[1:])
        result = result[:start] + new_lines + result[old_end:]

    target_file.write_text("".join(result))


def verify_subagent_fix(target_file: Path, reproduction_cmd: str) -> dict:
    repo_root = target_file.parent.parent.parent
    repro_passed = False
    if reproduction_cmd:
        try:
            r = subprocess.run(reproduction_cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=str(repo_root))
            repro_passed = r.returncode == 0
        except Exception:
            pass
    bench_passed = False
    try:
        b = subprocess.run([sys.executable, "-m", "benchmarks.benchmark_suite"], capture_output=True, text=True, timeout=120, cwd=str(repo_root))
        bench_passed = b.returncode == 0
    except Exception:
        pass
    tests_passed = False
    try:
        t = subprocess.run([sys.executable, "-m", "pytest", "tests/", "--tb=short", "-q"], capture_output=True, text=True, timeout=120, cwd=str(repo_root))
        tests_passed = t.returncode == 0
    except Exception:
        pass
    return {"reproduction_passed": repro_passed, "benchmark_passed": bench_passed, "unit_tests_passed": tests_passed}
