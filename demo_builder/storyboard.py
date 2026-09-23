"""Render a demo script as markdown and as a self-contained HTML storyboard.

The HTML is a single file: inline CSS, vanilla JS, no CDN, works offline.
"""
from __future__ import annotations

import html

from .models import DemoScript
from .scoring import score_script, summarize


def script_to_markdown(script: DemoScript) -> str:
    lines = [
        f"# Demo script: {script.title}",
        "",
        f"Persona: {script.persona}",
        f"Storyline: {script.storyline}",
        f"Value prop: {script.value_prop}",
        f"Total runtime: {script.total_seconds() // 60}m {script.total_seconds() % 60:02d}s",
        "",
    ]
    for i, s in enumerate(script.scenes, 1):
        lines.append(f"## Scene {i}: {s.title} [{s.beat}] ({s.timing_seconds}s)")
        lines.append(f"Benefit: {s.benefit}")
        lines.append("Talking points:")
        lines.extend(f"- {p}" for p in s.talking_points)
        lines.append("Actions:")
        lines.extend(f"- {a}" for a in s.actions)
        if s.cta:
            lines.append(f"Call to action: {s.cta}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


_CSS = """
body { font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
       max-width: 860px; margin: 0 auto; padding: 24px; color: #1f2937; background: #f8fafc; }
header.hero { background: #111827; color: #f9fafb; border-radius: 12px; padding: 28px; margin-bottom: 20px; }
header.hero h1 { margin: 0 0 8px; font-size: 28px; }
header.hero p { margin: 4px 0; color: #d1d5db; }
.meta { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px; }
.pill { background: #374151; border-radius: 999px; padding: 4px 14px; font-size: 13px; }
.pill.good { background: #065f46; } .pill.bad { background: #92400e; }
.scene { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
         padding: 20px 24px; margin-bottom: 16px; }
.scene.active { border: 2px solid #4f46e5; }
.scene-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.num { background: #4f46e5; color: #fff; border-radius: 50%; width: 28px; height: 28px;
       display: inline-flex; align-items: center; justify-content: center; font-weight: 700; }
.beat { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
        border-radius: 6px; padding: 3px 10px; color: #fff; }
.beat-hook { background: #b3541e; } .beat-setup { background: #2f6f9f; }
.beat-aha { background: #7a3fa0; } .beat-payoff { background: #2e7d4f; }
.time { margin-left: auto; color: #6b7280; font-size: 13px; }
.scene h2 { margin: 8px 0; font-size: 20px; }
.scene h3 { margin: 14px 0 6px; font-size: 14px; text-transform: uppercase;
            letter-spacing: 0.5px; color: #6b7280; }
.scene ul { margin: 4px 0 0; padding-left: 20px; }
.scene li { margin: 4px 0; }
.benefit { background: #ecfdf5; border-left: 4px solid #2e7d4f; padding: 8px 12px;
           margin-top: 12px; border-radius: 0 8px 8px 0; }
.cta { background: #eef2ff; border-left: 4px solid #4f46e5; padding: 8px 12px;
       margin-top: 12px; border-radius: 0 8px 8px 0; font-weight: 600; }
nav.controls { position: sticky; bottom: 16px; display: flex; justify-content: center;
               align-items: center; gap: 16px; margin-top: 8px; }
nav.controls button { background: #4f46e5; color: #fff; border: none; border-radius: 8px;
                      padding: 10px 22px; font-size: 15px; cursor: pointer; }
nav.controls button:hover { background: #4338ca; }
#pos { font-weight: 600; color: #4b5563; }
.hint { text-align: center; color: #9ca3af; font-size: 13px; margin-top: 8px; }
"""

_JS = """
var scenes = Array.prototype.slice.call(document.querySelectorAll('.scene'));
var idx = 0;
function show(i) {
  idx = (i + scenes.length) % scenes.length;
  scenes.forEach(function (s, k) { s.classList.toggle('active', k === idx); });
  document.getElementById('pos').textContent = (idx + 1) + ' / ' + scenes.length;
  scenes[idx].scrollIntoView({block: 'nearest', behavior: 'smooth'});
}
document.getElementById('prev').onclick = function () { show(idx - 1); };
document.getElementById('next').onclick = function () { show(idx + 1); };
document.addEventListener('keydown', function (e) {
  if (e.key === 'ArrowRight') show(idx + 1);
  if (e.key === 'ArrowLeft') show(idx - 1);
});
show(0);
"""


def _esc(text) -> str:
    return html.escape(str(text))


def _scene_card(i: int, s) -> str:
    points = "".join(f"<li>{_esc(p)}</li>" for p in s.talking_points)
    actions = "".join(f"<li>{_esc(a)}</li>" for a in s.actions)
    card = (
        f'<section class="scene" id="scene-{i + 1}">'
        f'<div class="scene-top"><span class="num">{i + 1}</span>'
        f'<span class="beat beat-{_esc(s.beat)}">{_esc(s.beat)}</span>'
        f'<span class="time">{s.timing_seconds // 60}m {s.timing_seconds % 60:02d}s</span></div>'
        f"<h2>{_esc(s.title)}</h2>"
        f"<h3>Talking points</h3><ul>{points}</ul>"
        f"<h3>Suggested actions</h3><ul>{actions}</ul>"
        f'<div class="benefit"><strong>Viewer benefit:</strong> {_esc(s.benefit)}</div>'
    )
    if s.cta:
        card += f'<div class="cta">Call to action: {_esc(s.cta)}</div>'
    return card + "</section>"


def render_storyboard(script: DemoScript, results=None) -> str:
    if results is None:
        results = score_script(script)
    passed, total = summarize(results)
    total_s = script.total_seconds()
    score_class = "good" if passed == total else "bad"
    cards = "\n".join(_scene_card(i, s) for i, s in enumerate(script.scenes))
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(script.title)} - Demo Storyboard</title>\n"
        "<style>" + _CSS + "</style>\n</head>\n<body>\n"
        '<header class="hero">'
        f"<h1>{_esc(script.title)}</h1>"
        f"<p><strong>Persona:</strong> {_esc(script.persona)}</p>"
        f"<p><strong>Storyline:</strong> {_esc(script.storyline)}</p>"
        f"<p><strong>Value prop:</strong> {_esc(script.value_prop)}</p>"
        '<div class="meta">'
        f'<span class="pill">{len(script.scenes)} scenes</span>'
        f"<span class=\"pill\">{total_s // 60}m {total_s % 60:02d}s total</span>"
        f'<span class="pill {score_class}">Checklist: {passed}/{total}</span>'
        "</div></header>\n"
        "<main>\n" + cards + "\n</main>\n"
        '<nav class="controls"><button id="prev">Previous</button>'
        '<span id="pos"></span><button id="next">Next</button></nav>\n'
        '<p class="hint">Tip: use the left and right arrow keys to step through scenes.</p>\n'
        "<script>" + _JS + "</script>\n</body>\n</html>\n"
    )
