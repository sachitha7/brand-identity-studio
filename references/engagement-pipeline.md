# The engagement pipeline

The ten-stage agency process, what each stage produces, and which tier
includes it. This is the map — `deliverables-spec.md` says how each artifact
is actually built.

## The three tiers

Confirm the tier before starting. Scope creep in branding is usually a tier
question that was never asked out loud, and the scope note in most contracts
says deliverables vary by package.

| | **Essential** | **Standard** | **Full** |
|---|---|---|---|
| Typical use | Startup, single founder, fast launch | SME with a real market position to defend | Funded brand, export, or a rebrand of a trading business |
| Stages | 1, 5, 9 (mini) | 1–3, 5–7, 9 | All 10 |
| Strategy | — | Positioning + platform | Full research report + personas |
| Logo | 1 concept, 1 revision | 3 concepts, 2 revisions | 3 concepts, 3 revisions + full file set |
| Applications | — | Stationery + social | Stationery, social, packaging/signage, digital |
| Guidelines | Mini (8–12 pages) | Standard (20–28 pages) | Full (30–45 pages) |
| Handover | Logo files only | Files + guidelines | Files, guidelines, training walkthrough, launch checklist |

Whatever the tier, **say in the proposal how many concepts and revision
rounds are included.** Unbounded revisions is how a fixed-fee branding job
turns into a loss.

## Stage 1 — Onboarding

*Owner: account/project lead. Every tier.*

Kickoff call, written brief, scope and timeline, signed contract or SOW.
Nothing creative starts until the brief is written down and the number of
concepts, revision rounds, timeline and file ownership are agreed. Those
four are the ones that cause disputes later.

**Produces:** project brief, timeline, signed SOW.

## Stage 2 — Discovery & Research

*Owner: strategist. Standard (light) / Full (complete).*

Stakeholder interviews, brand audit (if a rebrand), competitor research,
audience research.

Send the intake pack (`intake.md`) before this stage, not during it — the
client needs time to answer properly, and half the value is in making them
articulate things they've never written down.

**Produces:** research report, competitor audit, brand audit.

## Stage 3 — Brand Strategy

*Owner: strategist. Standard and Full.*

Positioning, values/mission/vision, audience personas, differentiation
angle, brand personality.

The differentiation angle is the load-bearing part: what this brand can
credibly claim that the named competitors cannot. If that sentence isn't
defensible, the visual work downstream has nothing to express.

**Produces:** positioning statement, brand platform, audience personas.

## Stage 4 — Creative Direction

*Owner: creative director. Full only.*

Mood boards and two to three distinct visual directions, presented for the
client to choose between — not one option presented as a fait accompli.

Generate mood boards cheaply and in volume (`z_image` / `nano_banana`, see
`model-selection.md`); this stage is about finding the route, not polishing.

**Produces:** mood boards, creative direction brief, chosen direction.

## Stage 5 — Visual Identity Design

*Owner: designer. Every tier.*

Logo concepts, colour palette, typography system, imagery style, revision
rounds.

If the client already has a logo, this stage becomes *documenting and
systematising* it rather than replacing it — see the engagement-type check
in `content-architecture.md`. Getting that wrong wastes the whole build.

**Produces:** primary logo, secondary/icon, colour palette, type system,
imagery direction.

## Stage 6 — Verbal Identity

*Owner: copywriter. Standard and Full.*

Name (if in scope), tagline, brand story, messaging pillars, tone of voice.

Tone of voice is only useful written in the brand's own voice, with real
do/don't pairs in the client's actual vocabulary. Generic tone-of-voice
pages get ignored.

**Produces:** name, tagline, brand story, messaging pillars, tone of voice
guide.

## Stage 7 — Applications

*Owner: designer. Standard (core) / Full (complete).*

Stationery (business card, letterhead, email signature, invoice template),
presentation template, social templates, packaging and signage if in scope.

This is where the identity either holds up or falls apart — an identity
that only works on its own logo sheet isn't finished.

**Produces:** stationery set, presentation template, social kit, packaging
and signage mockups.

## Stage 8 — Digital & Web

*Owner: digital designer. Full only.*

Website style guide, UI kit, ad templates.

A website style guide is not a website design — it's the rules a web build
must follow: type scale in px, spacing system, button and form states,
colour usage on screen (which differs from print: check contrast at actual
sizes).

**Produces:** website style guide, UI kit, ad templates.

## Stage 9 — Brand Guidelines

*Owner: designer, reviewed by creative director. Every tier, scaled.*

Compile everything approved into the rulebook, with explicit do's and
don'ts. Built to the page system in `page-system.md`.

A guideline page that only shows the right way is half a page. The misuse
page is the one people actually consult.

**Produces:** brand guidelines PDF.

## Stage 10 — Handover & Launch

*Owner: account lead. Full (and a reduced version for every tier).*

Package final files, walk the client through them, advise on rollout.

Run `logo_fileset.py` for the complete final-files matrix — colour, black
and reversed, in SVG/PDF/EPS/AI/PNG plus favicons. The reversed variant is
the one most often missing and the one the client needs first.

**Produces:** final file set, guidelines handover, launch checklist.

## Tracking

If the engagement runs across sessions or weeks, the
`anthropic-skills:brand-identity-workflow` skill tracks stage status,
owners and deliverables in a portable `project.json`. It tracks; this skill
produces. They compose — use both on a long engagement, this one alone for
a single deliverable.
