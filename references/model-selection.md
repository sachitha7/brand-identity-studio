# Choosing the right image model

Higgsfield exposes 30+ image models. Defaulting to one for everything is the
single biggest quality gap in AI-assisted brand work — a model tuned for
photoreal product shots will render a logo concept badly, and a model that
nails vector marks will produce a flat, lifeless packshot.

Pick per task from the table below. Every row was taken from the live model
catalogue (`models_explore`), not guessed.

## The matrix

| Creative task | Model | Key params | Why this one |
|---|---|---|---|
| **Logo concepts / exploration** | `recraft_v4_1` | `model_type: "vector"`, `colors: ["#hex", ...]` | Purpose-built for logos, typography and icons. Takes the brand palette as hex directly, so concepts arrive on-palette instead of needing correction. |
| **Icon / pictogram set** | `recraft_v4_1` | `model_type: "vector"` or `"utility_vector"` | Same engine, so a set generated together stays visually consistent — which is the whole point of an icon family. |
| **Patterns, graphic elements** | `recraft_v4_1` | `model_type: "utility_vector"`, `colors`, `background_color` | Flat, repeatable, palette-locked. |
| **Mood boards / direction options** | `z_image` or `nano_banana` | — | Stage 4 needs *volume* — twenty cheap options beat three expensive ones when you're still finding the direction. Save the good models for the chosen route. |
| **Logo on physical product / packaging** | `gpt_image_2_5` | `medias: [{role: "image_references"}]`, `quality: "high"`, `resolution: "2k"` | The verified reference-image technique (see `mockups.md`). Reproduces the real mark rather than inventing one. |
| **Anything with legible text on it** | `openai_hazel` or `nano_banana_pro` | — | Both are explicitly built for text rendering. Reach here when pack copy, a tagline or contact details must be readable. |
| **Stationery — card, letterhead** | `openai_hazel` | — | Best text rendering plus logo/typography handling; a business card is mostly small text. |
| **Clean front-facing packshot** | `recraft_v4_1` | `model_type: "utility"` | "Cleaner, flatter, front-facing and predictable" — exactly what a catalogue packshot needs, and what a cinematic model gets wrong. |
| **Lifestyle / UGC / people with product** | `soul_2` | `quality: "2k"` | Built for realistic UGC and editorial. Also the right model for audience-persona imagery in a strategy deck. |
| **Retail environment, signage in situ** | `soul_location` | — | Purpose-built for environments rather than objects. |
| **Campaign hero / key visual** | `soul_cinematic` or `cinematic_studio_2_5` | `resolution: "4k"` | Cinema-grade stills for the one image that leads a launch. |
| **Social / product ad templates** | `marketing_studio_image` | `resolution: "2k"` | Built for social ad formats; understands the genre. |
| **Cut out a product** | `image_background_remover` | — | Don't prompt for "white background" and hope — remove it deterministically. |
| **One hero → many aspect ratios** | `flux_2_pro_outpaint` | `expand_*` per side | Extends the *same* image rather than regenerating, so the social crop and the billboard are genuinely the same shot. |
| **Precise edit of an approved image** | `seedream_v5_pro` | `is_inpaint: true` | Instruction-based editing. Don't re-roll an approved image over a small fix. |
| **Large-format print asset** | `seedream_v4_5` (`quality: "high"`, ~6K) or `gpt_image_2_5` (`resolution: "4k"`) | — | Billboards and banners need the pixels. |

## Two settings that quietly cost you quality

**`gpt_image_2_5` defaults to `quality: "low"` and `resolution: "1k"`.** For
anything going in front of a paying client, set `quality` to `"high"` (or
`"max"` for a hero) and `resolution` to `"2k"` or `"4k"`. The default is a
draft setting. This is easy to miss because the output still looks
reasonable — it just isn't what the client is paying for.

**`background: "transparent"`** on `gpt_image_2_5` gives a cut-out asset
directly, which saves a background-removal round trip when you need a
product or element to drop onto another layout.

## Don't pass `use_unlim: true` blindly

Several models advertise `supports_unlim`, but whether *this* account can
spend unlimited generations right now is a separate question — check the
`unlim` block in a `models_explore` response. If it reads
`available: false`, passing `use_unlim: true` gets rejected rather than
silently falling back, and it caps `count` to 1 when it does apply. Omitting
it lets the server decide and ask.

## Cost discipline

Preflight with `get_cost: true` before a large batch — it returns the credit
cost without submitting. A 12-image batch at 4K costs meaningfully more than
the same batch at 1K, and on a client engagement you want that number before
you spend it, not after.

Use `generate_image_batch` for independent prompts (up to 12) rather than
twelve separate calls, then `jobs_wait` on the returned IDs.

## The rule that overrides all of the above

**Look at every generated image before it goes in a deliverable.** Model
choice improves the odds; it does not remove the QA gate in `mockups.md`.
A logo that came back subtly redrawn is still wrong no matter which model
produced it.
