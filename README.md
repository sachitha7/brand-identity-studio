# brand-identity-studio

A Claude Code skill for building professional brand identity documents —
strategy, logo system, colour and type specification, product/range
architecture, and photoreal application mockups — exported as a 16:9 PDF
brand book.

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
│   ├── content-architecture.md       what the book says, section order
│   ├── page-system.md                16:9 layout, colour sampling, type, PDF export
│   └── mockups.md                    the reference-image logo technique
├── scripts/
│   ├── build_pdf.py                  HTML → PDF via headless Chrome, page-count
│   │                                 and content verification, --split-render
│   │                                 fallback for a real Chrome paint-drop bug
│   ├── vectorize_logo.py             raster logo → scalable SVG
│   ├── grade_caps.py                 deterministic colour correction for mockups
│   └── composite_logo.py             fallback hand-compositing (wordmarks, touch-ups)
└── evals/
    ├── evals.json                    test prompts
    └── files/                        placeholder logos for the two test brands
```

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
