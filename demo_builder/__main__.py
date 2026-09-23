"""Command line interface: python -m demo_builder {plan|score|storyboard}"""
from __future__ import annotations

import argparse
import json
import sys

from .models import DemoScript
from .prd import from_idea, parse_prd
from .providers import PROVIDERS
from .scoring import render_report, score_script, summarize
from .storyboard import render_storyboard, script_to_markdown


def _load_script(path: str) -> DemoScript:
    with open(path, encoding="utf-8") as f:
        return DemoScript.from_dict(json.load(f))


def cmd_plan(args) -> int:
    if args.idea:
        prd = from_idea(args.idea)
    elif args.prd:
        with open(args.prd, encoding="utf-8") as f:
            prd = parse_prd(f.read())
    else:
        print("error: provide a PRD markdown file or --idea text", file=sys.stderr)
        return 2
    provider_cls = PROVIDERS.get(args.provider)
    if provider_cls is None:
        print(f"error: unknown provider '{args.provider}' "
              f"(available: {', '.join(sorted(PROVIDERS))})", file=sys.stderr)
        return 2
    script = provider_cls().generate(prd)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(script.to_dict(), f, indent=2)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(script_to_markdown(script))
        print(f"Wrote {args.md}")
    total = script.total_seconds()
    print(f"Wrote {args.out} "
          f"({len(script.scenes)} scenes, {total // 60}m {total % 60:02d}s)")
    return 0


def cmd_score(args) -> int:
    script = _load_script(args.script)
    results = score_script(script)
    report = render_report(script, results)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Wrote {args.md}")
    passed, total = summarize(results)
    print(report)
    print(f"Checklist: {passed}/{total} passed.")
    return 0


def cmd_storyboard(args) -> int:
    script = _load_script(args.script)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render_storyboard(script))
    print(f"Wrote {args.out}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="demo_builder",
        description="Turn a PRD or feature idea into an effective product demo.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="Generate a demo script from a PRD or idea.")
    p.add_argument("prd", nargs="?", help="Path to a PRD markdown file.")
    p.add_argument("--idea", help="Plain-text feature description (instead of a PRD file).")
    p.add_argument("-o", "--out", required=True, help="Output path for the script JSON.")
    p.add_argument("--md", help="Also write the script as markdown to this path.")
    p.add_argument("--provider", default="heuristic",
                   help=f"Provider to use (default: heuristic).")
    p.set_defaults(func=cmd_plan)

    s = sub.add_parser("score", help="Score a script against the best-practice checklist.")
    s.add_argument("script", help="Path to a script JSON file.")
    s.add_argument("--md", help="Write the checklist report as markdown to this path.")
    s.set_defaults(func=cmd_score)

    b = sub.add_parser("storyboard", help="Render a script as an HTML storyboard.")
    b.add_argument("script", help="Path to a script JSON file.")
    b.add_argument("-o", "--out", required=True, help="Output path for the HTML file.")
    b.set_defaults(func=cmd_storyboard)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
