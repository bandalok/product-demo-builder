"""Provider interface: ABC contract, heuristic behavior, registry."""
import pytest

from demo_builder.models import DemoScript
from demo_builder.prd import ParsedPRD, from_idea
from demo_builder.providers import PROVIDERS, HeuristicProvider, LLMProvider


def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_heuristic_generates_valid_script():
    prd = ParsedPRD(title="Feature", problem="It hurts.",
                    users="Support leads.", features=["Scores tickets"],
                    metrics=["40% faster"])
    script = HeuristicProvider().generate(prd)
    assert isinstance(script, DemoScript)
    assert len(script.scenes) == 6
    assert sum(1 for s in script.scenes if s.beat == "aha") == 1
    assert script.total_seconds() <= 12 * 60
    assert script.scenes[-1].cta.strip()
    assert all(s.benefit.strip() for s in script.scenes)
    assert len({s.storyline for s in script.scenes}) == 1


def test_heuristic_handles_empty_prd():
    script = HeuristicProvider().generate(ParsedPRD(title="Bare"))
    assert len(script.scenes) == 6
    assert script.persona  # falls back to a generic persona


def test_heuristic_works_from_idea():
    prd = from_idea("A dashboard that shows churn risk per account in one view.")
    script = HeuristicProvider().generate(prd)
    assert script.title
    assert len(script.scenes) == 6


def test_registry():
    assert PROVIDERS["heuristic"] is HeuristicProvider
    assert issubclass(HeuristicProvider, LLMProvider)
