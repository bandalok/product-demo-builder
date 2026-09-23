"""Provider registry. Add real-model providers here as they are built."""

from .base import LLMProvider
from .heuristic import HeuristicProvider

PROVIDERS = {
    "heuristic": HeuristicProvider,
}

__all__ = ["LLMProvider", "HeuristicProvider", "PROVIDERS"]
