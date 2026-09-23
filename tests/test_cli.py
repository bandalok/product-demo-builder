"""CLI smoke test: plan -> score -> storyboard on the demo PRD."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "demo" / "sample_prd.md"


def run(*args):
    proc = subprocess.run(
        [sys.executable, "-m", "demo_builder", *args],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def test_cli_end_to_end(tmp_path):
    assert PRD.exists(), "demo/sample_prd.md must exist for the smoke test"
    script_json = tmp_path / "script.json"
    script_md = tmp_path / "script.md"
    report_md = tmp_path / "report.md"
    board = tmp_path / "board.html"

    run("plan", str(PRD), "-o", str(script_json), "--md", str(script_md))
    data = json.loads(script_json.read_text())
    assert len(data["scenes"]) == 6

    out = run("score", str(script_json), "--md", str(report_md))
    assert "5/5" in out
    assert "rules passed" in report_md.read_text()

    run("storyboard", str(script_json), "-o", str(board))
    html_text = board.read_text()
    assert "<!DOCTYPE html>" in html_text
    assert "Demo Storyboard" in html_text
    assert script_md.read_text().startswith("# Demo script:")


def test_cli_idea_mode(tmp_path):
    script_json = tmp_path / "idea.json"
    run("plan", "--idea", "Churn radar flags at-risk accounts early.",
        "-o", str(script_json))
    assert json.loads(script_json.read_text())["title"]
