AI demo builder that helps product managers create effective product demos.

# demo-builder

Most product demos fail the same way: they open on a login screen, tour every
feature, and run long. This tool turns a PRD (or a rough feature description)
into a tight, story-driven demo: a scene-by-scene script, a score against
demo best practices, and a clickable storyboard you can present from.

## The story-arc method

Every generated script follows one fixed arc, because the structure is the
product:

1. **Hook** (1 min) - name the pain, not the login screen
2. **Aha moment** (2 min) - the key feature working, inside the first third
3. **How it works** (2 min) - the moving parts, each tied to the persona
4. **Proof** (1.5 min) - before-and-after, metrics not adjectives
5. **Objection** (1 min) - name the worry, show the off-ramp
6. **Close** (1 min) - restate the value prop, land one call to action

Total: 8m 30s. One persona, one storyline, every scene tied to a user benefit.

## Quickstart

Zero setup. Standard library only, no API keys.

```bash
python -m demo_builder plan demo/sample_prd.md -o /tmp/demo.json
python -m demo_builder score /tmp/demo.json
python -m demo_builder storyboard /tmp/demo.json -o /tmp/board.html
```

Or start from a rough idea instead of a PRD:

```bash
python -m demo_builder plan --idea "Churn radar flags at-risk accounts early." -o /tmp/demo.json
```

See `demo/` for a full worked example: sample PRD, generated script
(`script.json`, `script.md`), and storyboard (`storyboard.html`).

## The best-practice checklist

`score` checks every script against five rules and reports pass/fail with a
concrete fix for each failure:

| Rule | What it checks |
|---|---|
| Aha moment lands early | Exactly one `aha` scene, inside the first third |
| Total length within 12 minutes | Sum of scene timings is 12:00 or less |
| One storyline only | Every scene carries the same storyline label |
| Every scene ties to a user benefit | No scene without a stated viewer benefit |
| Ends with a clear call to action | Final scene names one concrete next step |

## Plugging in a real model

`demo_builder/providers/` defines the `LLMProvider` interface:

```python
from demo_builder.providers import LLMProvider
from demo_builder.models import DemoScript
from demo_builder.prd import ParsedPRD

class MyModelProvider(LLMProvider):
    name = "my-model"

    def generate(self, prd: ParsedPRD) -> DemoScript:
        # call your model here, return a DemoScript
        ...
```

Register it in `demo_builder/providers/__init__.py`:

```python
PROVIDERS = {"heuristic": HeuristicProvider, "my-model": MyModelProvider}
```

Then run with `python -m demo_builder plan prd.md -o out.json --provider my-model`.
The shipped `HeuristicProvider` is template and structure driven, so the tool
works fully offline; a model provider only needs to beat it on talking-point
quality, since story structure is enforced by the scorer either way.

## GitHub Pages

`docs/index.html` is the sample storyboard, ready to serve. To publish it:
repo Settings -> Pages -> Deploy from a branch -> select `main` and the
`/docs` folder. The page is a single self-contained file (inline CSS, vanilla
JS, no CDN), so it works as-is.

## Layout

```
demo_builder/      package: models, PRD parsing, scoring, storyboard, CLI
demo_builder/providers/   LLMProvider interface + heuristic default
tests/             pytest suite (story rules, parsing, scoring, providers, CLI)
demo/              sample PRD + generated script and storyboard
docs/              storyboard HTML, ready for GitHub Pages
```

Built by Alok Band.
