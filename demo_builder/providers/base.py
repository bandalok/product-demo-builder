"""Provider interface: how demo scripts get generated.

Ship with HeuristicProvider (stdlib only, zero setup). To plug in a real
model later, subclass LLMProvider and register it in PROVIDERS.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import DemoScript
from ..prd import ParsedPRD


class LLMProvider(ABC):
    """Generates a complete, story-structured DemoScript from a parsed PRD."""

    name = "base"

    @abstractmethod
    def generate(self, prd: ParsedPRD) -> DemoScript:
        """Return a complete demo script for the given brief."""
