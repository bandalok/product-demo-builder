"""PRD parsing: full docs, missing sections, heading synonyms, idea text."""
from demo_builder.prd import from_idea, parse_prd

FULL_PRD = """# Auto-Triage for the Support Inbox

## Problem
Agents drown in an unsorted inbox. Urgent tickets wait hours.

## Target users
Support leads at B2B SaaS companies.

## Key features
- AI urgency scoring
- One-click suggested replies
- SLA risk radar

## Success metrics
- First-response time down 40%
- SLA breaches down 60%
"""


def test_full_prd_parses():
    prd = parse_prd(FULL_PRD)
    assert prd.title == "Auto-Triage for the Support Inbox"
    assert "unsorted inbox" in prd.problem
    assert "Support leads" in prd.users
    assert prd.features == ["AI urgency scoring", "One-click suggested replies",
                            "SLA risk radar"]
    assert prd.metrics == ["First-response time down 40%", "SLA breaches down 60%"]
    assert prd.persona == "Support leads at B2B SaaS companies"


def test_missing_sections_get_defaults():
    prd = parse_prd("# Bare feature\n\n## Problem\nIt is slow.\n")
    assert prd.title == "Bare feature"
    assert prd.problem == "It is slow."
    assert prd.users == ""
    assert prd.features == []
    assert prd.metrics == []
    assert prd.persona == ""


def test_unknown_headings_ignored():
    prd = parse_prd("# T\n\n## Background\nSome history.\n\n## Problem\nReal pain.\n")
    assert prd.problem == "Real pain."
    assert "history" not in prd.problem


def test_heading_synonyms():
    prd = parse_prd("# T\n\n## Audience\nParents.\n\n## Metrics\n- NPS up 10\n")
    assert prd.users == "Parents."
    assert prd.metrics == ["NPS up 10"]


def test_numbered_bullets():
    prd = parse_prd("# T\n\n## Features\n1. First thing\n2. Second thing\n")
    assert prd.features == ["First thing", "Second thing"]


def test_prose_features_become_sentences():
    prd = parse_prd("# T\n\n## Features\nIt scores tickets. It drafts replies.\n")
    assert prd.features == ["It scores tickets.", "It drafts replies."]


def test_title_falls_back_to_first_line():
    prd = parse_prd("My cool feature\n\n## Problem\nSlow.\n")
    assert prd.title == "My cool feature"


def test_from_idea():
    prd = from_idea("Smart reminders nudge users before they churn. "
                    "It watches usage drops. It sends one timely nudge.")
    assert prd.title.startswith("Smart reminders")
    assert prd.problem.startswith("Smart reminders")
    assert len(prd.features) >= 1


def test_from_idea_empty():
    prd = from_idea("")
    assert prd.title == "Untitled feature"
