"""demo_builder: turn a PRD or feature idea into an effective product demo."""

from .models import DemoScript, Scene
from .prd import ParsedPRD, from_idea, parse_prd
from .providers import PROVIDERS, HeuristicProvider, LLMProvider
from .scoring import RuleResult, render_report, score_script, summarize
from .storyboard import render_storyboard, script_to_markdown

__all__ = [
    "DemoScript", "Scene", "ParsedPRD", "from_idea", "parse_prd",
    "PROVIDERS", "HeuristicProvider", "LLMProvider",
    "RuleResult", "render_report", "score_script", "summarize",
    "render_storyboard", "script_to_markdown",
]
