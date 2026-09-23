"""Heuristic provider: template + story-structure driven generation.

No model calls, stdlib only. The story arc is fixed so every script it
produces passes the best-practice checklist by construction:

  1. Hook      (60s)  - name the pain
  2. Aha       (120s) - the key feature working, inside the first third
  3. Setup     (120s) - the moving parts
  4. Payoff    (90s)  - proof the numbers move
  5. Setup     (60s)  - handle the obvious objection
  6. Payoff    (60s)  - restate the value prop, land the call to action

Total: 8m 30s, one storyline, every scene tied to a user benefit.
"""
from __future__ import annotations

from ..models import DemoScript, Scene
from ..prd import ParsedPRD
from .base import LLMProvider


def _short(text: str, limit: int = 100) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


class HeuristicProvider(LLMProvider):
    name = "heuristic"

    def generate(self, prd: ParsedPRD) -> DemoScript:
        persona = prd.persona or "your user"
        storyline = (
            f"One story: {persona} goes from buried in the problem "
            "to done in minutes."
        )
        key_feature = prd.features[0] if prd.features else "the core workflow"
        value_prop = self._value_prop(prd, persona)

        scenes = [
            Scene(
                title="Hook: name the pain",
                beat="hook",
                storyline=storyline,
                talking_points=[
                    "Open with the cost of the status quo, not with a login screen.",
                    f'"{_short(prd.problem, 140)}"' if prd.problem
                    else "Set up the painful starting point your user knows too well.",
                ],
                actions=[
                    "Land on the messy starting screen.",
                    "Show the manual workaround people use today.",
                ],
                timing_seconds=60,
                benefit=f"{persona} feels seen: the demo starts from their real day.",
            ),
            Scene(
                title="Aha moment: watch it work",
                beat="aha",
                storyline=storyline,
                talking_points=[
                    f"Do the one thing that changes everything: {_short(key_feature, 120)}.",
                    "Pause. Let the result land before you explain it.",
                ],
                actions=[
                    "Perform the key action live, in one unbroken flow.",
                    "Zoom in on the result. Say nothing for two seconds.",
                ],
                timing_seconds=120,
                benefit=f"{persona} sees the payoff in under two minutes.",
            ),
            Scene(
                title="How it works: the moving parts",
                beat="setup",
                storyline=storyline,
                talking_points=self._feature_points(prd),
                actions=[
                    "Walk through each capability exactly once.",
                    "Skip the settings page. Nobody ever bought on a settings page.",
                ],
                timing_seconds=120,
                benefit=f"{persona} trusts it: every piece maps to something they do.",
            ),
            Scene(
                title="Proof: the numbers move",
                beat="payoff",
                storyline=storyline,
                talking_points=self._metric_points(prd),
                actions=[
                    "Pull up the before-and-after view.",
                    "Point at the metric, not the chart chrome.",
                ],
                timing_seconds=90,
                benefit="Skeptics get evidence, not adjectives.",
            ),
            Scene(
                title="The objection you are thinking",
                beat="setup",
                storyline=storyline,
                talking_points=[
                    "Name the obvious worry: rollout effort, edge cases, trust.",
                    "Answer it with the smallest true thing you have.",
                ],
                actions=[
                    "Show the undo button and the off-ramp.",
                    "Show where a human stays in control.",
                ],
                timing_seconds=60,
                benefit=f"{persona} relaxes: the risk feels handled.",
            ),
            Scene(
                title="Close: restate the value",
                beat="payoff",
                storyline=storyline,
                talking_points=[
                    f"Restate it in one line: {_short(value_prop, 140)}.",
                    "Land the ending. Do not open a new topic.",
                ],
                actions=[
                    "Return to the result screen from the aha moment.",
                    "Leave that screen up while you talk.",
                ],
                timing_seconds=60,
                benefit="The value prop is the last thing they hear.",
                cta="Ask for one concrete next step: a two-week pilot with their own data.",
            ),
        ]
        return DemoScript(
            title=prd.title,
            storyline=storyline,
            persona=persona,
            value_prop=value_prop,
            scenes=scenes,
        )

    def _value_prop(self, prd: ParsedPRD, persona: str) -> str:
        if prd.problem:
            return (
                f"{prd.title} takes on {_short(prd.problem, 110)} "
                f"so {persona} gets the outcome without the busywork."
            )
        return (
            f"{prd.title} gives {persona} a faster, calmer way to get the job done."
        )

    def _feature_points(self, prd: ParsedPRD) -> list:
        if prd.features:
            return [f"Show it: {_short(f, 120)}." for f in prd.features[:3]]
        return [
            "Walk through each capability exactly once.",
            "Tie every click back to the persona's job to be done.",
        ]

    def _metric_points(self, prd: ParsedPRD) -> list:
        if prd.metrics:
            return [f"Metric to move: {_short(m, 120)}." for m in prd.metrics[:3]]
        return [
            "Show a before-and-after comparison.",
            "Tell one customer-style anecdote with a number in it.",
        ]
