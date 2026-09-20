---
name: brand-identity-studio
description: Build a professional brand identity document — brand strategy, logo system, colour and type specification, product/range architecture, and photoreal application mockups (packaging, signage, apparel, stationery) — exported as a 16:9 PDF brand book. Use this whenever the user asks for brand guidelines, a brand book, a rebrand or rebranding proposal, brand identity documentation, a style guide for a company or product, or wants an existing brand's visual system extended to new applications. Also trigger when the user wants a logo composited convincingly onto product mockups or packaging photography — this skill's reference-image technique produces materially better mockups than generating a blank scene and hand-compositing the logo afterward. Make sure to use this skill even if the user just says "make me a brand book" or "I need a logo on some mockups" without using the word "guidelines."
---

# Brand identity studio

Everything needed to take a business from "here's our logo" (or "here's
nothing yet") to a client-ready brand book: the strategy content, the
16:9 page system, and — the part that most visibly separates this from a
template — photoreal application mockups with the real logo file
integrated by the image model itself, not pasted on afterward.

This skill has three reference files and four scripts. Read the references
before building; use the scripts as you go, don't reimplement their logic.

## Before anything else: which engagement is this?

Ask, if it isn't obvious from context: is this **documenting an existing
brand** as-is, or **proposing a rebrand**? These produce different books
that can look deceptively similar if built carelessly — see
`references/content-architecture.md` § "Two kinds of engagement." Getting
this wrong (e.g. lovingly documenting a brand the client just told you had
failed commercially) wastes the whole build. When genuinely unclear, ask
the user rather than guess.

## The three references

| File | Read it for |
|---|---|
| `references/content-architecture.md` | What the book says: section order, writing rules, what gets a brand book rejected |
| `references/page-system.md` | How it's laid out: the 1920x1080 page grid, colour-sampling method, typography rules, the Chrome export pipeline |
| `references/mockups.md` | **The reference-image logo-compositing technique** — how to get a real logo onto photoreal packaging/signage/apparel without it coming out warped or subtly wrong, plus the "critical applications" checklist and a QA gate |

Read `mockups.md` before generating a single application-page image — it's
the difference between mockups that read as agency-made and ones that read
as AI-assisted.

## The four scripts

All in `scripts/`, all take `--help`, all tested against real files before
this skill shipped.

- **`build_pdf.py`** — exports the HTML brand book to PDF via headless
  Chrome and verifies the page count. Use this instead of shelling out to
  Chrome by hand; the page-count check catches overflow bugs immediately.
- **`vectorize_logo.py`** — traces a raster logo (PNG) into a scalable
  SVG, for when the only logo file the client has is low-resolution. Keep
  the traced SVG as the printer-facing artwork file; see the note in its
  docstring about why the brand book itself should usually still embed the
  PNG, not the SVG (a Chrome print export rasterises `<img src=svg>` at
  on-screen display size, which can be *lower* resolution than the source
  PNG).
- **`grade_caps.py`** — deterministically shifts a generated mockup's
  material colour (a metal cap, a foil block) to an exact brand hex, when
  the image model's own approximation doesn't land close enough. Preserves
  the surface's existing shading.
- **`composite_logo.py`** — the **fallback** hand-compositing tool, for
  wordmarks, touch-ups, or when no image-generation tool is connected.
  Read `mockups.md` first — for most mockups, the reference-image
  technique in that file beats this script outright.

## Process

1. Confirm which engagement this is (above), then gather what the brand
   actually has: existing logo files, product photography, palette,
   catalogue copy. Sample real colours from real artwork — never invent a
   palette when one already exists (`page-system.md` has the sampling
   method).
2. Write the strategy content first (`content-architecture.md`), before
   any layout work — the visual system is downstream of the positioning,
   not the other way round.
3. Build the HTML brand book at 1920x1080 per page (`page-system.md`).
4. For every application page, generate the mockup with the logo as a
   reference image (`mockups.md`) — upload the logo, call
   `generate_image` with `medias: [{value, role: "image_references"}]`
   (role name is model-specific; check rather than guess), and state
   explicitly in the prompt that the mark must be reproduced precisely.
   Run the QA gate in `mockups.md` on every result before wiring it in.
5. Check the "critical applications" list in `mockups.md` against what
   this brand's channels actually need — most drafts undershoot this list
   on the first pass.
6. Export with `build_pdf.py`, passing `--expect-pages` once you know the
   final count, so a future edit that silently overflows a page gets
   caught immediately rather than shipped.

## When Higgsfield isn't connected

The mockup technique in `mockups.md` needs an image-generation MCP tool
(this skill was built and verified against Higgsfield's `gpt_image_2_5`).
If nothing is connected: tell the user, point them at the one-time
`claude mcp login` setup in `mockups.md`'s Troubleshooting section (it
needs their interactive browser — you cannot complete it for them), and in
the meantime fall back to `composite_logo.py` or plain CSS/vector mockups.
Say plainly in the book (or to the user) that this is a fallback, not
silently ship the weaker result as if it were the intended outcome.
