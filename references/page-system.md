# Page system

The visual execution standard: a 16:9 page, a fixed body grid, and an
HTML-to-PDF pipeline that scales cleanly from screen to print. Pair with
`content-architecture.md` for what goes on each page and `mockups.md` for
photography.

## The page

Every page is **1920 x 1080**. Build the whole deck as one HTML file, pages
as stacked `.page` elements, scaled with **container query units** so one set
of numbers works at any viewport and at print size:

```css
.page {
  container-type: inline-size;
  aspect-ratio: 16 / 9;
  --u: 1cqw;              /* 1 unit = 1% of page width */
}
.page h1 { font-size: calc(var(--u) * 4.6); }
```

At ≤880px release the aspect ratio, stack to one column, and raise `--u` to
about `2.1cqw` so body copy stays above 13px on screen. Guard this behind
`@media screen` — an unguarded narrow-screen rule also fires inside the print
stylesheet and silently breaks pagination.

```
┌──┬──────────────────────────────────────────────────┐
│sp│   Headline            <- display face, top-left   │
│in│                                                   │
│e │   body column          visual field, right 2/3     │
│  │   (narrow measure)                                │
└──┴──────────────────────────────────────────────────┘
```

- **Spine**: a narrow vertical band down the left edge, brand colour or
  gradient, running the full page height. Carries the rotated
  `<Brand> | <Document>` footer.
- **Headline**: top-left, left margin ~8% of page width.
- **Body column**: left third, never wider than ~26% of page width — the
  narrow measure is what makes a page read as considered rather than dense.
- **Visual**: right two-thirds, optically centred in its own area.
- **Divider pages** break the rule deliberately: headline centred, no body
  copy, no spine — used between major sections (e.g. before "Applications").

Type sizes in units, as a starting scale: headline `4.6u`, section label
`1.05u` (tracked `0.22em`, uppercase), body `1.42u` at `1.62` leading, spec
caption `0.78u`, footer `0.82u`. Adjust to the chosen typefaces' actual
x-height rather than copying these blind.

## Colour specification

Sample real hex values out of the client's existing artwork — never eyedrop
a screenshot by eye and never invent a value that "looks about right":

```python
import pymupdf
from PIL import Image
from collections import Counter
page = pymupdf.open(src)[0]
page.get_pixmap(dpi=150).save(out)
Counter(Image.open(out).convert("RGB").getdata()).most_common(8)
```

Every swatch is published with **HEX, RGB and CMYK**, in that order, under a
named label; add a Pantone reference for any foil or spot colour, since foil
cannot be matched in process colour. Convert CMYK arithmetically
(`k = 1 - max(r,g,b)/255`), don't guess.

**Check every foreground/background pair for WCAG AA** (4.5:1 body text,
3:1 large text/graphics) and report the actual ratios on the colour-
proportion page — including any pair that *fails*, with the restriction
that follows from it (e.g. "approved for rules and 24px+ type only"). Hiding
a failing pair is worse than reporting it; the client needs to know before
someone puts it in a paragraph of body copy.

## Typography

Two faces, three jobs.

- **Primary / display** — headlines, the logotype's typographic cousin,
  pull quotes. Should carry the brand's personality on its own. Pick
  something the register actually calls for — a fragrance counter reads
  differently from a wellness blog; don't default to whatever looks premium
  in the abstract.
- **Secondary / text** — body, captions, labels, UI, every number. Must be
  legible small and boring on purpose.
- Load from Google Fonts only (the one host the Artifact/most sandboxed
  environments permit) and always declare a real fallback stack.
- Avoid Inter and Space Grotesk as the reflexive "safe" choice — they read
  as unconsidered precisely because they're everywhere.

## Export to PDF

Headless Chrome is the export path — it's the one local engine that honours
container queries, web fonts and CSS gradients together (`weasyprint` and
`wkhtmltopdf` do not).

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless --disable-gpu --window-size=1920,1080 --no-pdf-header-footer \
  --virtual-time-budget=20000 --print-to-pdf="out.pdf" "file:///path/doc.html"
```

Pair with a print stylesheet:

```css
@media print {
  @page { size: 1920px 1080px; margin: 0 }
  html, body { width: 1920px; background: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact }
  .page { width: 1920px; height: 1080px; aspect-ratio: auto;
    break-inside: avoid; break-after: page }
  .page:last-child { break-after: auto }
}
```

**Verify the page count matches expectation before calling the export done**
— a mismatch almost always means a page overflowed its 16:9 box and split
in two. `scripts/build_pdf.py` in this skill does this check automatically;
use it rather than shelling out to Chrome by hand.

## Mockups: vector/CSS vs. photoreal

CSS/vector mockups (drawn boxes, gradients, simple 3D transforms) are fast
and fine for early drafts, but they read as drawn, not photographed — flat
shadows, no material texture, no real light falloff. For a client paying
agency rates, this is usually the single biggest visible quality gap between
"AI-assisted" and "professional." See `mockups.md` for the technique that
closes it: real photography generation with the client's actual logo file
passed in as a reference image, not redrawn by hand.
