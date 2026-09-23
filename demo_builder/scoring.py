"""Best-practice checklist scoring for demo scripts.

Every rule reports pass/fail plus a concrete fix, so a failing script tells
the presenter exactly what to change.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .models import DemoScript

MAX_TOTAL_SECONDS = 12 * 60  # demos must run 12 minutes or less


@dataclass
class RuleResult:
    rule: str
    passed: bool
    detail: str
    fix: str = ""


def _fmt(seconds: int) -> str:
    return f"{seconds // 60}m {seconds % 60:02d}s"


def score_script(script: DemoScript) -> list:
    results = []
    n = len(script.scenes)

    # 1. Aha moment lands early (within the first third)
    aha = [i for i, s in enumerate(script.scenes) if s.beat == "aha"]
    if not aha:
        results.append(RuleResult(
            "Aha moment lands early", False,
            "No scene uses the 'aha' beat.",
            "Add exactly one scene with beat 'aha' inside the first third of the script.",
        ))
    elif len(aha) > 1:
        scenes = ", ".join(str(i + 1) for i in aha)
        results.append(RuleResult(
            "Aha moment lands early", False,
            f"{len(aha)} scenes use the 'aha' beat (scenes {scenes}).",
            "Keep exactly one aha moment; fold the extras into the main one.",
        ))
    else:
        i = aha[0]
        cutoff = max(1, math.ceil(n / 3))  # first third, in 1-based scene numbers
        if i < n / 3:
            results.append(RuleResult(
                "Aha moment lands early", True,
                f"Aha moment is scene {i + 1} of {n}, inside the first third.",
            ))
        else:
            results.append(RuleResult(
                "Aha moment lands early", False,
                f"Aha moment is scene {i + 1} of {n}; the first third ends at scene {cutoff}.",
                f"Move the aha moment to scene {cutoff} or earlier.",
            ))

    # 2. Total length within 12 minutes
    total = script.total_seconds()
    if total <= MAX_TOTAL_SECONDS:
        results.append(RuleResult(
            "Total length within 12 minutes", True,
            f"Total runtime {_fmt(total)}.",
        ))
    else:
        over = total - MAX_TOTAL_SECONDS
        results.append(RuleResult(
            "Total length within 12 minutes", False,
            f"Total runtime {_fmt(total)} exceeds 12m 00s by {_fmt(over)}.",
            f"Trim {_fmt(over)}: cut the weakest scene or shorten talking points.",
        ))

    # 3. One storyline only
    labels = {s.storyline.strip() for s in script.scenes}
    if n == 0:
        results.append(RuleResult(
            "One storyline only", False,
            "The script has no scenes.",
            "Add scenes that follow one persona and one job to be done.",
        ))
    elif "" in labels:
        results.append(RuleResult(
            "One storyline only", False,
            "Some scenes have no storyline label.",
            "Give every scene the same storyline label so the arc stays checkable.",
        ))
    elif len(labels) > 1:
        results.append(RuleResult(
            "One storyline only", False,
            f"Found {len(labels)} storylines: {', '.join(sorted(labels))}.",
            "Rewrite around one persona and one job to be done; move the rest to a second demo.",
        ))
    else:
        results.append(RuleResult(
            "One storyline only", True,
            f"All {n} scenes follow one storyline.",
        ))

    # 4. Every scene ties to a user benefit
    missing = [i + 1 for i, s in enumerate(script.scenes) if not s.benefit.strip()]
    if not missing:
        results.append(RuleResult(
            "Every scene ties to a user benefit", True,
            f"All {n} scenes name a user benefit.",
        ))
    else:
        results.append(RuleResult(
            "Every scene ties to a user benefit", False,
            f"Scene(s) {missing} state no user benefit.",
            "For each flagged scene add one line: what does the viewer gain from watching this?",
        ))

    # 5. Ends with a clear call to action
    if n and script.scenes[-1].cta.strip():
        results.append(RuleResult(
            "Ends with a clear call to action", True,
            "The final scene names a concrete next step.",
        ))
    else:
        results.append(RuleResult(
            "Ends with a clear call to action", False,
            "The final scene has no call to action.",
            "End with one concrete ask, e.g. 'Start a two-week pilot with your own data.'",
        ))

    return results


def summarize(results: list) -> tuple:
    passed = sum(1 for r in results if r.passed)
    return passed, len(results)


def render_report(script: DemoScript, results: list) -> str:
    passed, total = summarize(results)
    lines = [f"# Demo checklist: {script.title}", "",
             f"**{passed}/{total} rules passed.**", ""]
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        lines.append(f"## [{mark}] {r.rule}")
        lines.append(r.detail)
        if r.fix:
            lines.append(f"Fix: {r.fix}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
