"""Core data models for demo scripts."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field


VALID_BEATS = ("hook", "setup", "aha", "payoff")


@dataclass
class Scene:
    title: str
    beat: str  # one of hook | setup | aha | payoff
    storyline: str  # the single narrative thread every scene belongs to
    talking_points: list
    actions: list  # suggested clicks / actions for the presenter
    timing_seconds: int
    benefit: str  # the user benefit this scene demonstrates
    cta: str = ""  # call to action; meaningful on the final scene

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title", ""),
            beat=data.get("beat", "setup"),
            storyline=data.get("storyline", ""),
            talking_points=list(data.get("talking_points", [])),
            actions=list(data.get("actions", [])),
            timing_seconds=int(data.get("timing_seconds", 60)),
            benefit=data.get("benefit", ""),
            cta=data.get("cta", ""),
        )


@dataclass
class DemoScript:
    title: str
    storyline: str
    persona: str
    value_prop: str
    scenes: list = field(default_factory=list)

    def to_dict(self):
        return {
            "title": self.title,
            "storyline": self.storyline,
            "persona": self.persona,
            "value_prop": self.value_prop,
            "scenes": [s.to_dict() for s in self.scenes],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title", ""),
            storyline=data.get("storyline", ""),
            persona=data.get("persona", ""),
            value_prop=data.get("value_prop", ""),
            scenes=[Scene.from_dict(s) for s in data.get("scenes", [])],
        )

    def total_seconds(self):
        return sum(s.timing_seconds for s in self.scenes)
