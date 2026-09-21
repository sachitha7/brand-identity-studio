"""Scaffold a client engagement folder in the agency's standard structure.

Run once at Stage 1, before any creative work. Having the folders exist from
day one is what stops a handover turning into an archaeology exercise —
files land where they belong as they're produced, rather than being sorted
at the end when nobody remembers which logo version was approved.

    python init_engagement.py --client "Hexona Ceylon" --tier full --out D:/Hexona

Tiers scope which folders are created (see references/engagement-pipeline.md):
    essential   brief, identity, guidelines, final files
    standard    adds research, strategy, verbal, applications
    full        every stage including creative direction and digital

Writes an ENGAGEMENT.md at the root recording client, tier, date and the
scope questions that must be answered in the contract before creative work
starts — number of concepts, revision rounds, timeline, file ownership.
Those four are what disputes are made of.
"""

import argparse
import datetime
import pathlib
import re
import sys

ALL_FOLDERS = [
    ("00-brief", "Signed SOW, project brief, timeline, intake responses", "all"),
    ("01-research", "Research report, competitor audit, brand audit", "standard"),
    ("02-strategy", "Positioning, brand platform, personas", "standard"),
    ("03-direction", "Mood boards, direction options, chosen route", "full"),
    ("04-identity", "Logo concepts, palette, type, imagery direction", "all"),
    ("05-verbal", "Name, tagline, brand story, messaging, tone of voice", "standard"),
    ("06-applications", "Stationery, social, packaging, signage", "standard"),
    ("07-digital", "Website style guide, UI kit, ad templates", "full"),
    ("08-guidelines", "Brand guidelines document (HTML source + PDF)", "all"),
    ("09-final-files", "Logo file set, handover pack, launch checklist", "all"),
    ("assets", "Working source: logo masters, photography, generated imagery", "all"),
]

TIER_RANK = {"essential": 0, "standard": 1, "full": 2}
REQ_RANK = {"all": 0, "standard": 1, "full": 2}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--client", required=True, help="Client name as it should appear")
    ap.add_argument("--tier", required=True, choices=["essential", "standard", "full"])
    ap.add_argument("--out", required=True, type=pathlib.Path, help="Engagement root directory")
    ap.add_argument("--engagement", default=None,
                     help="Short project name, e.g. 'brand identity' or 'rebrand'")
    args = ap.parse_args()

    tier_rank = TIER_RANK[args.tier]
    root = args.out
    root.mkdir(parents=True, exist_ok=True)

    created = []
    for folder, purpose, required in ALL_FOLDERS:
        if REQ_RANK[required] > tier_rank:
            continue
        d = root / folder
        d.mkdir(exist_ok=True)
        readme = d / "README.txt"
        if not readme.exists():
            readme.write_text(f"{folder}\n{'=' * len(folder)}\n\n{purpose}\n", encoding="utf-8")
        created.append(folder)

    engagement = args.engagement or "brand identity"
    today = datetime.date.today().isoformat()
    doc = root / "ENGAGEMENT.md"
    if doc.exists():
        print(f"ENGAGEMENT.md already exists at {doc} — left untouched.")
    else:
        doc.write_text(
            f"# {args.client} — {engagement}\n\n"
            f"- **Tier:** {args.tier}\n"
            f"- **Opened:** {today}\n"
            f"- **Slug:** {slugify(args.client)}\n\n"
            "## Confirm in the contract before creative work starts\n\n"
            "These four are what disputes are made of. Fill them in, don't leave them implied.\n\n"
            "- [ ] **Number of logo concepts presented:** \n"
            "- [ ] **Revision rounds included:** \n"
            "- [ ] **Timeline / key dates:** \n"
            "- [ ] **File ownership and usage rights on handover:** \n\n"
            "## Engagement type\n\n"
            "- [ ] Documenting an existing brand (systematise what exists)\n"
            "- [ ] Rebrand (replace a position that has failed commercially)\n\n"
            "Getting this wrong wastes the whole build — confirm it with the client in\n"
            "writing, not by inference.\n\n"
            "## Scope notes\n\n"
            "Packaging / signage / merchandise in scope?  \n"
            "Naming in scope?  \n"
            "Anything explicitly excluded?  \n",
            encoding="utf-8",
        )

    print(f"Scaffolded {args.tier} engagement for {args.client} at {root}")
    for f in created:
        print(f"  {f}")
    print(f"\nNext: complete ENGAGEMENT.md, then send the intake pack "
          f"(see references/intake.md) before Stage 2.")


if __name__ == "__main__":
    main()
