"""Story structure rules: aha timing, single storyline, length cap."""
import pytest

from demo_builder.models import DemoScript, Scene
from demo_builder.prd import ParsedPRD
from demo_builder.providers import HeuristicProvider
from demo_builder.scoring import score_script


def make_scene(i, beat="setup", storyline="one story", benefit="a benefit",
               seconds=60, cta=""):
    return Scene(title=f"Scene {i}", beat=beat, storyline=storyline,
                 talking_points=["point"], actions=["click"],
                 timing_seconds=seconds, benefit=benefit, cta=cta)


def make_script(scenes):
    return DemoScript(title="T", storyline="one story", persona="P",
                      value_prop="V", scenes=scenes)


def rule(results, name):
    return next(r for r in results if r.rule == name)


def test_heuristic_script_passes_structure():
    prd = ParsedPRD(title="Feature", problem="Pain.", users="Busy analysts.",
                    features=["Auto-triage"], metrics=["Faster by 40%"])
    script = HeuristicProvider().generate(prd)
    results = score_script(script)
    assert rule(results, "Aha moment lands early").passed
    assert rule(results, "One storyline only").passed
    assert rule(results, "Total length within 12 minutes").passed
    assert rule(results, "Every scene ties to a user benefit").passed
    assert rule(results, "Ends with a clear call to action").passed
    # aha is scene 2 of 6 -> inside the first third
    assert script.scenes[1].beat == "aha"


def test_late_aha_fails_with_fix():
    scenes = [make_scene(i, beat="aha" if i == 5 else "setup") for i in range(9)]
    scenes[-1].cta = "Buy now."
    r = rule(score_script(make_script(scenes)), "Aha moment lands early")
    assert not r.passed
    assert "scene 6 of 9" in r.detail
    assert r.fix  # concrete fix present


def test_no_aha_fails():
    scenes = [make_scene(i) for i in range(3)]
    scenes[-1].cta = "Buy now."
    r = rule(score_script(make_script(scenes)), "Aha moment lands early")
    assert not r.passed
    assert "No scene" in r.detail


def test_two_aha_moments_fail():
    scenes = [make_scene(i, beat="aha" if i in (1, 4) else "setup") for i in range(6)]
    scenes[-1].cta = "Buy now."
    r = rule(score_script(make_script(scenes)), "Aha moment lands early")
    assert not r.passed
    assert "2 scenes" in r.detail


def test_multiple_storylines_fail():
    scenes = [make_scene(i, storyline="story A" if i < 3 else "story B") for i in range(6)]
    scenes[1].beat = "aha"
    scenes[-1].cta = "Buy now."
    r = rule(score_script(make_script(scenes)), "One storyline only")
    assert not r.passed
    assert "story A" in r.detail and "story B" in r.detail


def test_overlong_script_fails():
    scenes = [make_scene(i, seconds=300) for i in range(3)]  # 15 minutes
    scenes[0].beat = "aha"
    scenes[-1].cta = "Buy now."
    r = rule(score_script(make_script(scenes)), "Total length within 12 minutes")
    assert not r.passed
    assert "15m 00s" in r.detail


def test_exactly_12_minutes_passes():
    scenes = [make_scene(i, seconds=120) for i in range(6)]  # exactly 12m
    scenes[1].beat = "aha"
    scenes[-1].cta = "Buy now."
    assert rule(score_script(make_script(scenes)),
                "Total length within 12 minutes").passed


def test_empty_script_fails_gracefully():
    results = score_script(make_script([]))
    assert len(results) == 5
    by_rule = {r.rule: r for r in results}
    # The meaningful rules fail; length/benefit are vacuously satisfied.
    assert not by_rule["Aha moment lands early"].passed
    assert not by_rule["One storyline only"].passed
    assert not by_rule["Ends with a clear call to action"].passed
