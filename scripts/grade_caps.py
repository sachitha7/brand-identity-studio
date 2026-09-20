"""Shift a generated mockup's metal/material colour to an exact brand hex.

An image model's "champagne gold" or "matte basalt" is its own
approximation — close in lightness, off in hue/saturation, and not
consistent between generations of the same prompt. This grades a region
deterministically toward the real target while leaving VALUE (lightness)
untouched, so the surface's existing highlight/shadow shading survives —
that shading is what reads as "real metal," and overwriting it produces a
flat, plasticky patch instead of a colour-corrected photograph.

    python grade_caps.py <image.jpg> <target_hex> <x0> <y0> <x1> <y1> [<x0> <y0> <x1> <y1> ...]

Pass one or more boxes (read their pixel coordinates off a coordinate grid
overlaid on the image — see the docstring note below). Overwrites the image
in place; make a copy first if you want to compare before/after.

REAL TRAP, found the hard way: a rectangular box is never a round object's
actual silhouette, so its corners usually catch some out-of-focus
background. Left ungated, a flat hue/saturation shift turns that low-
saturation bokeh into a visible flat-coloured rectangle — the box's own
edges become visible as a seam. The `s_lo` saturation floor below exists
specifically to stop this: only pixels that were already reasonably
saturated (i.e. already metal-toned, not smooth background) get shifted.
If you still see a rectangle after grading, tighten the box before raising
the floor — the box was probably too generous, not the floor too low.

To find box coordinates: render the image with a coordinate grid overlaid
(matplotlib, or PIL ImageDraw with gridlines every 50-100px + coordinate
labels), inspect it, then read off the corners of the region you want to
grade. Don't guess coordinates from the ungridded image.
"""

import argparse
import pathlib

import cv2
import numpy as np
from PIL import Image


def target_hs(hex_value):
    hex_value = hex_value.lstrip("#")
    rgb = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0, 0]
    return float(hsv[0]), float(hsv[1])


def grade_box(img, box, target_h, target_s, blend=0.85, v_lo=55, v_hi=248, s_lo=22):
    x0, y0, x1, y1 = box
    sub = img[y0:y1, x0:x1].astype(np.uint8)
    hsv = cv2.cvtColor(sub, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # Leave the brightest specular highlights and the darkest cast shadow
    # alone (v_lo/v_hi) — recolouring those breaks the illusion of a
    # reflective surface. The s_lo floor is the anti-bounding-box-leak
    # guard described in the module docstring.
    mask = (v > v_lo) & (v < v_hi) & (s > s_lo)

    hsv[..., 0] = np.where(mask, target_h, h)
    hsv[..., 1] = np.where(mask, s * (1 - blend) + target_s * blend, s)
    img[y0:y1, x0:x1] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=pathlib.Path)
    ap.add_argument("target_hex")
    ap.add_argument("box", nargs="+", type=int,
                     help="One or more x0 y0 x1 y1 quadruples")
    ap.add_argument("--blend", type=float, default=0.85)
    args = ap.parse_args()

    if len(args.box) % 4 != 0:
        ap.error("box coordinates must come in groups of 4 (x0 y0 x1 y1)")
    boxes = [tuple(args.box[i:i + 4]) for i in range(0, len(args.box), 4)]

    target_h, target_s = target_hs(args.target_hex)
    img = np.array(Image.open(args.image).convert("RGB"))
    for box in boxes:
        img = grade_box(img, box, target_h, target_s, blend=args.blend)
    Image.fromarray(img).save(args.image, quality=92)
    print(f"{args.image.name}: {len(boxes)} region(s) graded toward {args.target_hex}")


if __name__ == "__main__":
    main()
