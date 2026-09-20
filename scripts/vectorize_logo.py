"""Trace a raster logo (PNG with alpha) into a scalable SVG.

A client's only logo file is often a low-resolution PNG pulled from a PDF or
a screenshot. That's fine for embedding in a brand book (which is fixed at
1920x1080 print size), but a printer setting a shop fascia or a vehicle
wrap needs outlines. This traces the alpha channel into cubic Bezier paths
via a Catmull-Rom fit, so it stays smooth rather than faceted.

    python vectorize_logo.py <logo.png> <output.svg> [--color "#a837af"]

Verify the result against the source before handing it off — check with:

    python -c "
    import pymupdf, numpy as np
    from PIL import Image
    d = pymupdf.open('<output.svg>'); pdf = d.convert_to_pdf()
    p = pymupdf.open('pdf', pdf)
    src = Image.open('<logo.png>').convert('RGBA'); w, h = src.size
    pix = p[0].get_pixmap(matrix=pymupdf.Matrix(w/p[0].rect.width, h/p[0].rect.height), alpha=True)
    vec = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples).resize((w, h))
    a = np.array(src)[...,3] > 128; b = np.array(vec)[...,3] > 128
    print('IoU vs source: %.4f' % ((a & b).sum() / (a | b).sum()))
    "

An IoU below ~0.9 usually means EPSILON is too coarse for the mark's finest
detail (thin strokes, serifs) — lower it and re-run.

NOTE ON PDF EMBEDDING: if this SVG will be referenced by <img src=...> in an
HTML page you later print to PDF via Chrome, check the exported PDF's
embedded image resolution before assuming the SVG "worked." Chrome
rasterises <img src="*.svg"> at its ON-SCREEN DISPLAY SIZE when printing —
a monogram shown at 190px on a 1920px page embeds at ~190px, which is often
LOWER resolution than the original PNG would have embedded at. If that
happens, link the PNG in the HTML instead and keep this SVG only as the
separate artwork file handed to a printer for large-format work.
"""

import argparse
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image

SCALE = 4       # upscale factor before tracing, for sub-pixel contour detail
EPSILON = 1.2   # polyline simplification in upscaled pixels (~0.3px at source)
MIN_AREA = 40   # drop specks left behind by the alpha key, in upscaled pixels


def catmull_rom_to_bezier(points):
    n = len(points)
    d = [f"M{points[0][0]:.2f},{points[0][1]:.2f}"]
    for i in range(n):
        p0, p1, p2, p3 = (points[(i + k) % n] for k in (-1, 0, 1, 2))
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    d.append("Z")
    return "".join(d)


def trace(png_path, svg_path, color):
    image = Image.open(png_path).convert("RGBA")
    width, height = image.size
    alpha = np.array(image)[..., 3]
    big = cv2.resize(alpha, (width * SCALE, height * SCALE), interpolation=cv2.INTER_CUBIC)
    _, mask = cv2.threshold(big, 128, 255, cv2.THRESH_BINARY)

    # RETR_CCOMP keeps holes (e.g. inside an "O") as their own contours;
    # evenodd fill renders them as holes rather than filled-in blobs.
    contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    paths = []
    for contour in contours:
        if cv2.contourArea(contour) < MIN_AREA:
            continue
        simplified = cv2.approxPolyDP(contour, EPSILON, True)
        if len(simplified) < 3:
            continue
        points = [(p[0][0] / SCALE, p[0][1] / SCALE) for p in simplified]
        paths.append(catmull_rom_to_bezier(points))

    if not paths:
        sys.exit(f"Traced nothing from {png_path.name} — check the alpha channel isn't empty.")

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img">\n'
        f'  <path fill="{color}" fill-rule="evenodd" d="{"".join(paths)}"/>\n'
        f"</svg>\n"
    )
    svg_path.write_text(svg, encoding="utf-8")
    print(f"{svg_path.name}: {len(paths)} contours, {len(svg):,} bytes")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png", type=pathlib.Path)
    ap.add_argument("svg", type=pathlib.Path)
    ap.add_argument("--color", default="#000000", help="Fill colour for the traced path")
    args = ap.parse_args()
    if not args.png.exists():
        sys.exit(f"Missing {args.png}")
    trace(args.png, args.svg, args.color)


if __name__ == "__main__":
    main()
