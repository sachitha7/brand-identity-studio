# Photoreal mockups

How to get the client's real logo onto photoreal application mockups —
cartons, bags, signage, apparel, stationery — without it coming out warped,
smeared, or subtly wrong. This is the part of a brand book that most
visibly separates "AI-assisted" from "an agency built this," and it is easy
to get backwards.

## The core technique: reference image, not hand-compositing

**Do not** generate a blank product photo and then perspective-warp the
logo onto it yourself in Python. That was the default approach before this
technique was verified, and it reliably produces a flat, sticker-like
decal — hard edges, no wrap around curved glass, no play with the surface's
own lighting. Manual compositing also multiplies the chances of a layout
bug (text overlapping, a bounding box leaking onto out-of-focus background)
for every single mockup.

**Do**: pass the client's actual logo file to the image model as a
**reference image** and let the model integrate it into the generated scene
directly. Tested back to back against hand-compositing in a real
engagement — same subject, same lighting brief — the reference-image result
reproduced the mark with its proportions intact, correct perspective, and
real material shading (foil catching light, ink sitting in paper grain,
embossing with a believable bevel). The hand-composited version, even after
several rounds of fixing real bugs, never matched it.

### Verified call pattern (Higgsfield MCP, `gpt_image_2_5`)

```
1. Upload the logo file:
   mcp__higgsfield__media_upload  -> upload_url + media_id
   PUT the file bytes to upload_url (curl, from wherever the bytes live —
     never relay them through your own context as base64)
   mcp__higgsfield__media_confirm(type: "image", media_id)

2. Generate with the logo as a reference image:
   mcp__higgsfield__generate_image({
     model: "gpt_image_2_5",
     aspect_ratio: "16:9",
     medias: [{ value: "<media_id>", role: "image_references" }],
     prompt: "Using the exact logo mark shown in the reference image
       (describe it in one clause — do not just say 'the logo') —
       reproduce it precisely, do not redraw or reinterpret it — <where
       and how it should appear: material, finish, placement> ...
       <scene, materials, lighting, palette constraints> ..."
   })
```

Two things about the `medias` role matter and are easy to get wrong:

- The role name is model-specific. `gpt_image_2_5` wants
  `image_references`, not `reference` — a plausible-sounding guess errors
  out. Check `models_explore.get` (or the tool's own error message, which
  names the allowed roles) rather than assuming.
- **State explicitly in the prompt that the mark must be reproduced
  precisely, not redrawn.** Without that instruction the model still uses
  the reference as inspiration and subtly reinterprets the mark — close
  enough to fool a glance, wrong enough that it isn't the client's actual
  logo.

### When hand-compositing is still the right call

- **Wordmarks or long text lockups** where the reference-image approach
  hasn't been tested as thoroughly — generate the product blank instead,
  then composite the exact wordmark PNG with alpha blending (no
  perspective warp needed if you also ask for a frontal, non-angled shot).
- **A touch-up on an otherwise-good generation** — the mark is 90% right
  but sits 20px off-centre. Don't regenerate the whole shot; composite a
  correction.
- **No image-generation tool is connected at all.** Fall back to CSS/vector
  mockups (see `page-system.md`) and say so plainly in the book rather than
  silently shipping a lower bar. If Higgsfield specifically isn't
  connected, the fix is usually one `claude mcp login <server>` away — see
  the Troubleshooting note at the end of this file before assuming the
  fallback is necessary.

## Colour-accuracy note

An image model's idea of "champagne gold" or "matte basalt" is its own
approximation, and it will not exactly match a hex value in your palette —
nor will it be consistent from one generation to the next, even with an
identical prompt. If a mockup needs to land on an *exact* brand colour
(a metal cap, a foil block), grade it deterministically afterward: shift
hue and saturation toward the target while leaving value (lightness)
untouched, so the surface's own shading — the thing that reads as "real
metal" — survives the correction. `scripts/grade_caps.py` does this; see
its docstring for the one real trap (a rectangular grading box always
catches some out-of-focus background at its corners — add a saturation
floor to the mask so low-saturation bokeh doesn't get swept into a flat
colour block).

## The "critical applications" checklist

A book that only shows a business card and a tote bag reads as thin next
to what a paying client expects. Cover, at minimum, whichever of these the
brand's actual channels call for — not all of them apply to every business,
but check the list rather than stopping at the first three that come to
mind:

- **Packaging**: primary container/carton, retail bag
- **Stationery**: business card, letterhead
- **People**: staff ID card, staff apparel (embroidered/printed, small)
- **Environment**: signage (a fascia panel externally lit reads as premium;
  an internally backlit box reads as the tier below), retail/shelf
  presence
- **Small-format**: stickers (as a sheet, not a single roll)
- **Digital**: social post templates, app icon / profile avatar
- Category-specific extras where relevant: gift box, notebook, mug/cup,
  uniform beyond a single shirt, vehicle livery, a mascot/character if the
  brand has one

Each gets its own page: one clear specification sentence (material, size,
finish) plus one governing rule that would stop someone getting it wrong
(e.g. "never internally illuminated — a backlit panel is the fastest way
to look like the tier below").

## QA gate — run this before calling any mockup done

Zoom into the logo in every generated or composited mockup and check:

- **Letterforms survived.** A monogram or wordmark can come back subtly
  wrong — a stroke merged, a serif dropped — even from a reference-image
  generation. Compare directly against the source file, not from memory.
- **No garbled text.** Product names, sizes, taglines baked into a prompt
  can render as near-miss gibberish. If a shot needs legible text beyond
  the logo, say so explicitly in the prompt and check character-by-character.
- **No box-shadow-as-solid-rectangle.** A hard-edged colour block where a
  soft shadow was intended is a sign a CSS `box-shadow` printed literally
  rather than rendering as a shadow — use `filter: drop-shadow(...)` in
  any CSS mockup, and for a generated image, check the corners of any
  bounding-box edit for a leaked flat-colour rectangle (see the
  colour-accuracy note above).
- **No clipped art.** A monogram running off the edge of a carton or panel
  reads as broken immediately, and reads as unfinished worse than no logo
  at all.
- **Consistent palette across every application.** A mismatched accent
  colour between the carton page and the bag page is the kind of thing a
  client notices on the second read, not the first.

## Troubleshooting: Higgsfield not connected

If the MCP tools aren't available in this session:

1. `claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp`
   (safe to re-run if already added)
2. `claude mcp login higgsfield` — opens a browser OAuth flow. This
   **cannot** run from inside a non-interactive tool call; tell the user
   to run it themselves in their own terminal.
3. After login, the tools may not appear until the session restarts, or
   until `/mcp reconnect higgsfield` is run inside Claude Code.

This is a one-time setup per machine/account — once connected, it persists
across projects and sessions.
