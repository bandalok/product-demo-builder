"""Scoring checklist: each rule's pass/fail and fix quality."""
from demo_builder.models import DemoScript, Scene
from demo_builder.scoring import render_report, score_script, summarize


def scene(**kw):
    base = dict(title="S", beat="setup", storyline="story",
                talking_points=["p"], actions=["a"],
                timing_seconds=60, benefit="benefit", cta="")
    base.update(kw)
    return Scene(**base)


def script(scenes):
    return DemoScript(title="T", storyline="story", persona="P",
                      value_prop="V", scenes=scenes)


def passing_script():
    scenes = [scene() for _ in range(6)]
    scenes[1] = scene(beat="aha")
    scenes[5] = scene(cta="Start a pilot.")
    return script(scenes)


def test_all_rules_pass_on_good_script():
    results = score_script(passing_script())
    passed, total = summarize(results)
    assert (passed, total) == (5, 5)


def test_benefit_rule_flags_scene_numbers():
    scenes = [scene() for _ in range(4)]
    scenes[1] = scene(beat="aha")
    scenes[2] = scene(benefit="")
    scenes[3] = scene(cta="Go.")
    r = next(x for x in score_script(script(scenes))
             if x.rule == "Every scene ties to a user benefit")
    assert not r.passed
    assert "3" in r.detail
    assert r.fix


def test_cta_rule_checks_final_scene():
    scenes = [scene() for _ in range(4)]
    scenes[1] = scene(beat="aha")
    scenes[0] = scene(cta="Early ask.")  # CTA in the wrong place
    r = next(x for x in score_script(script(scenes))
             if x.rule == "Ends with a clear call to action")
    assert not r.passed
    assert r.fix


def test_fixes_present_on_every_failure():
    scenes = [scene(storyline="a" if i < 2 else "b", benefit="", timing_seconds=600)
              for i in range(4)]  # fails storyline, benefit, length, aha, cta
    results = score_script(script(scenes))
    assert all(r.fix for r in results if not r.passed)


def test_report_renders():
    report = render_report(passing_script(), score_script(passing_script()))
    assert "5/5 rules passed" in report
    assert "[PASS] Aha moment lands early" in report
