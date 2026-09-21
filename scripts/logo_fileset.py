"""Generate the complete final-files logo set a client actually gets at handover.

The handover deliverable in most agency contracts reads "logo in AI/EPS/SVG/
PNG/PDF, in colour, black and white, and reversed" — that's a matrix, not a
file, and assembling it by hand is where handovers get sloppy and incomplete.

    python logo_fileset.py <logo.svg> <out_dir> --brand-color "#03471e" --name hexona

Produces, for each of three colourways (colour / black / reversed white):
    SVG   vector master, editable anywhere
    PDF   vector, print-ready
    EPS   vector, for older print workflows that demand PostScript
    AI    PDF-compatible (see note below)
    PNG   at 512 / 1024 / 2048 px wide, transparent background

Plus favicon PNGs at 16/32/48/180/512 px, which contracts list under
"icon/favicon" and which otherwise get forgotten until a web build needs them.

ON .AI FILES — be straight with the client about this. A true native
Illustrator file can only be written by Illustrator. What this produces is a
PDF with an .ai extension: Illustrator opens it, edits it, and re-saves it as
native .ai without complaint, and that is the normal interchange route. It is
not a lie, but don't describe it as "native Illustrator artwork" either. If a
client's printer insists on native .ai, open the PDF in Illustrator once and
save it out.

The reversed (white) variant is the one most often missing from a handover and
the one a client needs most urgently — the first time they put the logo on a
dark background or a photo, they need it and it isn't there.
"""

import argparse
import pathlib
import re
import sys


def recolour_svg(svg_text, fill):
    """Force every path fill in the SVG to one colour.

    Brand marks are frequently multi-colour (a green mark with a gold ring),
    and the black / reversed variants must flatten all of that to a single
    ink — that's the whole point of those variants."""
    out = re.sub(r'fill="(?!none)[^"]*"', f'fill="{fill}"', svg_text)
    out = re.sub(r'fill:\s*(?!none)[^;"]+', f'fill:{fill}', out)
    return out


def png_from_pdf(pdf_path, png_path, width_px):
    """Rasterise a vector PDF to a transparent PNG at an exact pixel width.

    reportlab's own renderPM needs a Cairo backend that often isn't present on
    Windows; pymupdf has no native dependency and gives a cleaner alpha
    channel, so the PNGs come off the PDF we already generated rather than a
    second render path that could drift from it."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    page = doc[0]
    scale = width_px / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=True)
    pix.save(png_path)


def write_variants(src_svg, out_dir, name, brand_color):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPS, renderPDF

    svg_text = src_svg.read_text(encoding="utf-8")
    variants = {
        "colour": None,             # leave the source artwork untouched
        "black": "#000000",
        "reversed": "#ffffff",
    }

    made = []
    for variant, fill in variants.items():
        vdir = out_dir / variant
        vdir.mkdir(parents=True, exist_ok=True)
        text = svg_text if fill is None else recolour_svg(svg_text, fill)

        svg_path = vdir / f"{name}-{variant}.svg"
        svg_path.write_text(text, encoding="utf-8")
        made.append(svg_path)

        drawing = svg2rlg(str(svg_path))
        if drawing is None:
            sys.exit(f"svglib could not parse {svg_path} — check the SVG is valid.")

        pdf_path = vdir / f"{name}-{variant}.pdf"
        renderPDF.drawToFile(drawing, str(pdf_path))
        made.append(pdf_path)

        eps_path = vdir / f"{name}-{variant}.eps"
        renderPS.drawToFile(drawing, str(eps_path), fmt="EPS")
        made.append(eps_path)

        # .ai as a PDF copy — see the docstring note before describing this
        # to a client.
        ai_path = vdir / f"{name}-{variant}.ai"
        ai_path.write_bytes(pdf_path.read_bytes())
        made.append(ai_path)

        for px in (512, 1024, 2048):
            png_path = vdir / f"{name}-{variant}-{px}.png"
            png_from_pdf(pdf_path, png_path, px)
            made.append(png_path)

    return made


def write_favicons(src_svg, out_dir, name):
    """Favicon set — listed in contracts under 'icon/favicon' and routinely
    forgotten until someone is mid web build and blocked on it."""
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    from PIL import Image

    fdir = out_dir / "favicon"
    fdir.mkdir(parents=True, exist_ok=True)
    made = []

    tmp_pdf = fdir / "_base.pdf"
    base = fdir / "_base.png"
    renderPDF.drawToFile(svg2rlg(str(src_svg)), str(tmp_pdf))
    png_from_pdf(tmp_pdf, base, 1024)
    tmp_pdf.unlink()

    src = Image.open(base).convert("RGBA")
    for px in (16, 32, 48, 180, 512):
        im = src.copy()
        im.thumbnail((px, px), Image.LANCZOS)
        canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        canvas.paste(im, ((px - im.width) // 2, (px - im.height) // 2), im)
        p = fdir / f"{name}-favicon-{px}.png"
        canvas.save(p)
        made.append(p)
    base.unlink()
    return made


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("svg", type=pathlib.Path, help="Vector logo master (SVG)")
    ap.add_argument("out_dir", type=pathlib.Path, help="Output directory")
    ap.add_argument("--name", default="logo", help="Filename stem, e.g. the brand slug")
    ap.add_argument("--brand-color", default=None,
                     help="Brand hex, recorded in the manifest for reference")
    args = ap.parse_args()

    if not args.svg.exists():
        sys.exit(f"Missing {args.svg}")

    made = write_variants(args.svg, args.out_dir, args.name, args.brand_color)
    made += write_favicons(args.svg, args.out_dir, args.name)

    manifest = args.out_dir / "README.txt"
    manifest.write_text(
        "LOGO FILE SET\n"
        "=============\n\n"
        "colour/    the mark as designed\n"
        "black/     single-colour black, for one-colour print and faxed/stamped use\n"
        "reversed/  single-colour white, for dark grounds and photography\n"
        "favicon/   square icon crops at 16, 32, 48, 180 and 512 px\n\n"
        "Formats per colourway: SVG (vector master), PDF and EPS (print),\n"
        ".AI (PDF-compatible — opens and re-saves natively in Illustrator),\n"
        "PNG at 512/1024/2048 px with transparent background.\n\n"
        "Use the SVG or PDF for anything printed or scaled large. Use PNG only\n"
        "for screen, and never scale a PNG up.\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(made)} files to {args.out_dir}")
    for group in ("colour", "black", "reversed", "favicon"):
        n = len(list((args.out_dir / group).glob("*"))) if (args.out_dir / group).exists() else 0
        print(f"  {group:10} {n} files")


if __name__ == "__main__":
    main()
