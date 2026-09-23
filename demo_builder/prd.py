"""Parse a PRD markdown file (tolerant of missing sections) or plain idea text."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


# Normalized heading text -> section key. Unknown headings are ignored.
HEADINGS = {
    "problem": "problem",
    "the problem": "problem",
    "users": "users",
    "target users": "users",
    "audience": "users",
    "who it's for": "users",
    "key features": "features",
    "features": "features",
    "what it does": "features",
    "capabilities": "features",
    "success metrics": "metrics",
    "metrics": "metrics",
    "success criteria": "metrics",
    "goals": "metrics",
}


@dataclass
class ParsedPRD:
    title: str
    problem: str = ""
    users: str = ""
    features: list = field(default_factory=list)
    metrics: list = field(default_factory=list)

    @property
    def persona(self) -> str:
        if not self.users:
            return ""
        return self.users.split(".")[0].strip()


def _sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _bullets(lines: list) -> list:
    items = []
    for line in lines:
        m = re.match(r"\s*(?:[-*]|\d+[.)])\s+(.*)", line)
        if m:
            items.append(m.group(1).strip())
    return items


def _first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:80]
    return "Untitled feature"


def parse_prd(text: str) -> ParsedPRD:
    """Parse PRD markdown. Missing sections become empty defaults; unknown
    headings are skipped. The title is the first level-1 heading."""
    title = ""
    sections: dict = {}
    current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        heading = re.match(r"#{1,4}\s+(.*)", line)
        if heading:
            heading_text = heading.group(1).strip()
            if not title and re.match(r"#\s+", line):
                title = heading_text
            current = HEADINGS.get(heading_text.lower())
            if current is not None:
                sections.setdefault(current, [])
            continue
        if current and line:
            sections[current].append(line)

    def text_of(key: str) -> str:
        return " ".join(sections.get(key, [])).strip()

    feature_lines = sections.get("features", [])
    metric_lines = sections.get("metrics", [])
    return ParsedPRD(
        title=title or _first_line(text),
        problem=text_of("problem"),
        users=text_of("users"),
        features=_bullets(feature_lines) or _sentences(text_of("features")),
        metrics=_bullets(metric_lines) or _sentences(text_of("metrics")),
    )


def from_idea(text: str) -> ParsedPRD:
    """Build a minimal brief from a plain-text feature description."""
    text = text.strip()
    sents = _sentences(text)
    title = sents[0][:70] if sents else "Untitled feature"
    features = [s for s in sents[1:] if len(s) > 12][:4]
    if not features and sents:
        features = [sents[0]]
    return ParsedPRD(title=title, problem=text, features=features)
