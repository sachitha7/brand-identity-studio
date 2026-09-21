# Deliverables specification

Every artifact an engagement can produce, how it's built, and where it goes.
Pair with `engagement-pipeline.md` (which stage, which tier) and
`model-selection.md` (which image model).

Everything ships as **PDF** for client-facing documents, with the editable
HTML source kept alongside so it can be revised later without rebuilding.

## Folder structure

Scaffold this at the start of an engagement, not at handover:

```
<client>/
├── 00-brief/            signed SOW, project brief, timeline, intake responses
├── 01-research/         research report, competitor audit, brand audit
├── 02-strategy/         positioning, brand platform, personas
├── 03-direction/        mood boards, direction options, chosen route
├── 04-identity/         logo concepts, palette, type, imagery direction
├── 05-verbal/           name, tagline, brand story, messaging, tone of voice
├── 06-applications/     stationery, social, packaging, signage
├── 07-digital/          website style guide, UI kit, ad templates
├── 08-guidelines/       the brand guidelines document (source + PDF)
├── 09-final-files/      logo file set, handover pack, launch checklist
└── assets/              working source: logo masters, photography, generated imagery
```

Numbered so the folder reads in engagement order in any file browser — the
client opens this once, months later, and needs to find things without you.

## The deliverables

### Strategy

| Deliverable | Built as | Notes |
|---|---|---|
| Research report | PDF (HTML source) | Competitor set with real evidence — pricing, positioning, where they're weak. Web research plus the client's intake answers. |
| Positioning statement | Page in strategy PDF | One paragraph, defensible. Names the competitor it beats and on what. |
| Brand platform | PDF | Values, mission, vision, personality. Each value needs a behaviour attached or it's wallpaper. |
| Audience personas | PDF, 2–4 personas | Real buying context, not demographics theatre. Persona imagery via `soul_2`. |

### Core identity

| Deliverable | Built as | Notes |
|---|---|---|
| Primary logo | SVG master + full file set | Concepts via `recraft_v4_1` (`model_type: "vector"`). If the client has a logo, vectorise theirs (`vectorize_logo.py`) rather than replacing it. |
| Secondary logos | SVG | Horizontal lockup, stacked, mark-only — whichever the real applications need. |
| Icon / favicon | PNG set | `logo_fileset.py` produces 16/32/48/180/512 px. |
| Logo usage rules | Pages in guidelines | Clear-space in `X` units derived from the mark, minimum sizes in mm *and* px, misuse examples drawn wrong. |

### Visual system

| Deliverable | Built as | Notes |
|---|---|---|
| Colour palette | Pages in guidelines | HEX, RGB, CMYK per colour; Pantone for any spot/foil. Sample from real artwork, never invent. Report real WCAG ratios including failures. |
| Typography | Pages in guidelines | Display + text face, full scale with sizes/weights/tracking. Google Fonts unless the client owns a licence. |
| Imagery & photography style | Pages + reference shots | Rules plus example frames. Include explicit prohibitions. |
| Graphic elements, patterns | SVG/PNG + guideline pages | `recraft_v4_1` (`model_type: "utility_vector"`) with the brand hex passed in. |
| Iconography | SVG/PNG set | Generate the whole set in one batch so the family stays consistent. |

### Verbal identity

| Deliverable | Built as | Notes |
|---|---|---|
| Brand name | Strategy PDF | Only if in scope. Check domain and trademark availability before recommending — say plainly that a formal trademark search is a lawyer's job, not this document's. |
| Tagline | Guidelines | |
| Brand story | PDF | |
| Messaging pillars | PDF | Three or four, each with proof. |
| Tone of voice guide | Guideline pages | Three do/don't pairs in the brand's real vocabulary. |

### Stationery & collateral

| Deliverable | Built as | Notes |
|---|---|---|
| Business card | PDF artwork + mockup | Mockup via `openai_hazel` (text rendering) or `gpt_image_2_5` + reference image. Specify size, stock, finish. |
| Letterhead | PDF artwork + mockup | A4 with margins and type spec stated. |
| Email signature | HTML + PNG preview | HTML so it can actually be pasted into a mail client. |
| Invoice template | PDF | Often forgotten; it's the document a client's customers see most. |
| Presentation template | PDF (HTML source) | Title, section, content, data slides at minimum. |

### Digital

| Deliverable | Built as | Notes |
|---|---|---|
| Social profile kit | PNG set, correct pixel sizes | Profile image, cover images per platform the client actually uses. |
| Social templates | PDF + PNG | Post, story, carousel. Via `marketing_studio_image`. |
| Website style guide | PDF | Type scale in px, spacing system, button/form states, on-screen colour use. Not a page design. |
| UI kit | PDF spec | Components with states documented. |
| Ad templates | PNG/PDF per format | Standard IAB sizes plus the platforms in use. |

### Print & physical *(if in scope)*

| Deliverable | Built as | Notes |
|---|---|---|
| Packaging | Mockup + spec pages | Front/back panel architecture, mandatory fields, material spec. |
| Signage | Mockup + spec | Include illumination spec — externally lit vs internally backlit changes the tier a brand reads as. |
| Brochures | PDF template | |
| Uniforms | Mockup + spec | Embroidery size and single-colour rule; gradients don't survive fabric. |
| Merchandise | Mockups | Only what the client will actually produce. |

### Guidelines & final files

| Deliverable | Built as | Notes |
|---|---|---|
| Brand guidelines | PDF via `build_pdf.py` | 16:9. Scale page count to tier. Verify with `--expect-pages`. |
| Final logo files | `logo_fileset.py` | Colour/black/reversed × SVG/PDF/EPS/AI/PNG, plus favicons and a README the client can follow. |
| Launch checklist | PDF | What to update and in what order — signage, social, email, invoices, vehicle, packaging. Sequenced so the brand doesn't appear half-changed. |

## Two honesty rules

**`.ai` files.** What's produced is a PDF with an `.ai` extension.
Illustrator opens and re-saves it natively, which is the standard
interchange route — but don't describe it as native Illustrator artwork.

**Generated imagery.** Mockups illustrate how the identity is applied. If a
shot will be used in customer-facing marketing as though it were a
photograph of a real product, it needs to be a real photograph. Put that
distinction in the guidelines rather than leaving the client to discover it.
