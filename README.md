# brand-identity-studio

A Claude Code skill that runs a full brand identity engagement the way an
agency does — discovery, strategy, visual and verbal identity, applications,
digital, the guidelines document, and the complete final-file handover —
scoped to an Essential, Standard or Full package and delivered as
client-ready PDFs plus a proper logo file set.

## Install

Drop this directory into `~/.claude/skills/` (or clone it there directly):

```bash
git clone https://github.com/sachitha7/brand-identity-studio ~/.claude/skills/brand-identity-studio
```

Claude Code discovers it automatically and offers it as `/brand-identity-studio`,
or triggers it on requests like "build brand guidelines for X" or "put our
logo on some packaging mockups."

## What makes this different

Most AI-assisted brand books fall down in the same place: the mockups. A
generated blank product photo with a logo pasted on afterward looks pasted
on — flat shadows, no material texture, hard edges.

This skill's core technique is passing the real logo file to the image
model as a **reference image** and letting the model integrate it into the
generated scene directly, rather than generating a blank surface and
hand-compositing the logo in Python. Verified back to back against
hand-compositing on a real engagement: the reference-image result reproduced
the mark with proportions intact, correct perspective, and real material
shading (foil catching light, ink in the paper grain, an embossed bevel) —
the hand-composited version never matched it, even after several rounds of
bug fixes.

See `references/mockups.md` for the exact verified call pattern, a
"critical applications" checklist most drafts undershoot, and a QA gate to
run before calling any mockup done.

## Structure

```
brand-identity-studio/
├── SKILL.md                          entry point — read this first
├── references/
│   ├── engagement-pipeline.md        10 stages × 3 tiers, what each produces
│   ├── deliverables-spec.md          every deliverable, how built, where it lands
│   ├── intake.md                     client questionnaire, interview guide
│   ├── model-selection.md            which image model for which creative task
│   ├── mockups.md                    the reference-image logo technique + QA gate
│   ├── content-architecture.md       what the guidelines doc says, section order
│   └── page-system.md                16:9 layout, colour sampling, type, PDF export
├── scripts/
│   ├── init_engagement.py            scaffolds the client folder structure by tier
│   ├── build_pdf.py                  HTML → PDF via headless Chrome, page-count
│   │                                 AND content verification, --split-render
│   │                                 fallback for a real Chrome paint-drop bug
│   ├── logo_fileset.py               full handover matrix: colour/black/reversed
│   │                                 × SVG/PDF/EPS/AI/PNG + favicons
│   ├── vectorize_logo.py             raster logo → scalable SVG
│   ├── grade_caps.py                 deterministic colour correction for mockups
│   └── composite_logo.py             fallback hand-compositing (wordmarks, touch-ups)
└── evals/
    ├── evals.json                    test prompts
    └── files/                        placeholder logos for the two test brands
```

## Packages

| | Essential | Standard | Full |
|---|---|---|---|
| Stages | 1, 5, 9 | 1–3, 5–7, 9 | all 10 |
| Strategy | — | positioning + platform | research report + personas |
| Applications | — | stationery + social | + packaging, signage, digital |
| Guidelines | 8–12 pp | 20–28 pp | 30–45 pp |

## Choosing image models

Defaulting to one model for everything is the biggest quality gap in
AI-assisted brand work. `references/model-selection.md` maps each task to
the right model from the live catalogue — `recraft_v4_1` in vector mode for
logos, icons and patterns (it takes the brand hex palette directly),
`gpt_image_2_5` with reference images for logo-on-product mockups,
`openai_hazel` where text must be legible, `soul_2` for lifestyle and
persona imagery, `z_image` for cheap mood-board volume, and so on.

Every script takes `--help` and has been run against real files, not just
syntax-checked. `build_pdf.py`'s docstring in particular documents a real,
reproducible headless-Chrome bug (a page silently dropping its painted
content in a large multi-page export) and the split-render-and-merge fix for
it — worth reading before assuming a blank page in your own build is a
markup bug.

## Requires

- An image-generation MCP tool that supports reference images (built and
  verified against Higgsfield's `gpt_image_2_5`). Without one, the skill
  falls back to `composite_logo.py` or plain CSS/vector mockups — weaker,
  and the skill says so rather than silently shipping the fallback as if it
  were the intended result.
- `pymupdf`, `opencv-python`, `numpy`, `Pillow` for the bundled scripts.
- Google Chrome or Microsoft Edge for the PDF export.

## License

MIT.
