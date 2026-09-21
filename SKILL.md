---
name: brand-identity-studio
description: Run a full brand identity engagement the way a professional agency does — discovery and research, brand strategy and positioning, visual identity, verbal identity, applications, digital, the guidelines document, and the complete final-file handover — scoped to an Essential, Standard or Full package and delivered as client-ready PDFs plus a proper logo file set. Use this whenever the user asks for brand guidelines, a brand book, a brand identity, a rebrand, a style guide, logo files for handover, packaging or stationery or social templates for a client, or wants an existing brand's system documented and extended. Also trigger when the user wants a logo put convincingly onto product mockups or packaging photography, or asks which image model to use for a given creative task. Make sure to use this skill even if the user only says "make me a brand book", "do the branding for this client", or "I need our logo on some mockups" without naming stages or deliverables.
---

# Brand identity studio

Runs a client branding engagement end to end and produces the actual
deliverables — not a plan for them. Everything client-facing ships as PDF,
with editable HTML source kept alongside so it can be revised without
rebuilding. Creative imagery comes from Higgsfield, choosing the right model
per task rather than defaulting to one.

## Start here, every time

**1. Confirm the engagement type.** Documenting an existing brand, or
replacing one? These produce different books that look deceptively similar
if built carelessly. If the client says their current brand, product or site
has *failed commercially*, they want what replaces it — faithfully
documenting what exists is then the wrong deliverable, however accurate.
When it isn't obvious, ask.

**2. Confirm the tier** — Essential, Standard or Full
(`references/engagement-pipeline.md`). Scope creep in branding is almost
always a tier question nobody asked out loud.

**3. Confirm concepts, revision rounds, timeline and file ownership.** Those
four cause the disputes. `init_engagement.py` writes them into an
ENGAGEMENT.md checklist so they can't be skipped silently.

**4. Scaffold the folders** before producing anything:

```bash
python scripts/init_engagement.py --client "Client Name" --tier full --out <dir>
```

**5. Send the intake pack** (`references/intake.md`) before discovery, and
audit whatever assets the client supplies. Client "artwork" is frequently a
concept render with garbled placeholder text in it — read every word before
reproducing any of it, and flag what's wrong rather than carrying the error
into a deliverable.

## The references

| File | Read it for |
|---|---|
| `references/engagement-pipeline.md` | The 10 stages, what each produces, and which tier includes it |
| `references/deliverables-spec.md` | Every deliverable, how it's built, the folder it lands in |
| `references/intake.md` | Client questionnaire, stakeholder interview guide, asset request list |
| `references/model-selection.md` | **Which Higgsfield model for which creative task** — logos, mockups, mood boards, lifestyle, ads |
| `references/mockups.md` | The reference-image logo technique, applications checklist, QA gate |
| `references/content-architecture.md` | What the guidelines document says, section order, writing rules |
| `references/page-system.md` | The 1920×1080 page grid, colour sampling, typography, PDF export |

Read `model-selection.md` before generating any imagery and `mockups.md`
before any application mockup. Those two carry the quality difference.

## The scripts

All in `scripts/`, all take `--help`, all run against real files before
shipping.

- **`init_engagement.py`** — scaffolds the client folder structure by tier
- **`build_pdf.py`** — HTML → PDF via headless Chrome, verifies page count
  *and* that every page actually painted content; `--split-render` works
  around a real Chrome paint-drop bug documented in its docstring
- **`logo_fileset.py`** — the complete handover matrix: colour/black/reversed
  × SVG/PDF/EPS/AI/PNG, plus favicons and a client-readable README
- **`vectorize_logo.py`** — raster logo → scalable SVG, when the client's
  only file is a low-res PNG
- **`grade_caps.py`** — shifts a generated mockup's material colour to an
  exact brand hex, preserving the shading that makes it read as real
- **`composite_logo.py`** — fallback hand-compositing, for wordmarks and
  touch-ups only; the reference-image technique beats it for most mockups

## Producing the work

Do the actual creative work at each stage — write the positioning, design
the system, generate the imagery, build the documents. Tracking is not the
deliverable.

Two habits that separate this from generic output:

**Ground everything in the client's own material.** Sample colours from
their real artwork rather than inventing a palette. Use their SKU names,
their ingredient claims, their vocabulary. A book written in generic brand
language signals it wasn't written for them.

**State real limitations rather than hiding them.** A colour that fails
WCAG contrast, an ingredient percentage awaiting confirmation, an
inconsistency between two of their own product photos — these belong on the
page, framed as what to resolve. A brand book that only shows what already
works is worth less than one that also says what to fix.

## When Higgsfield isn't connected

The imagery technique needs an image-generation MCP tool (built and verified
against Higgsfield). If none is connected, tell the user, point them at the
one-time `claude mcp login` setup in `mockups.md`, and fall back to
`composite_logo.py` or CSS/vector mockups meanwhile — saying plainly that
it's a fallback rather than shipping the weaker result as if it were the
intended one.

Figma is deliberately not a dependency: on a View/Starter seat the MCP
server allows only 20 tool calls per *month*, nowhere near enough to produce
design files per client. Everything here is PDF plus HTML source instead.
