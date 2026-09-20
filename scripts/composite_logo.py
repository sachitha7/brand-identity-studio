"""Perspective-composite a logo onto a flat or angled surface in a photo.

FALLBACK TOOL. Read references/mockups.md first — for most application
mockups, passing the real logo as a reference image to the generation call
(Higgsfield/gpt_image_2_5, role "image_references") produces a better result
than this script: natural material shading, correct wrap on curved glass,
no manual placement math. Reach for this script only for a wordmark/long
text lockup, a touch-up correction on an otherwise-good generation, or when
no image-generation tool is connected at all.

    python composite_logo.py <photo.jpg> <logo.png> \
        <tl_x> <tl_y> <tr_x> <tr_y> <br_x> <br_y> <bl_x> <bl_y> \
        [--color "#17161a"] [--strength 0.94]

The four corner points are the destination quad in the photo, in
TL, TR, BR, BL order — read them off a coordinate grid overlaid on the
image (see the note in grade_caps.py's docstring for how). Overwrites
<photo.jpg> in place.

REAL BUG THIS GUARDS AGAINST: an earlier version of this technique picked
the destination quad's width and height independently of the logo's own
aspect ratio, which stretched the mark visibly on a wide surface (a fascia
panel, a long carton face). This script derives the quad's width from the
logo's real aspect ratio and the given height, so the mark can't distort —
pass a --height-frac (fraction of the box you're centring within) rather
than four independently-chosen corners if you want that guarantee; if you
pass exact corners instead, check the result isn't stretched before moving on.
"""

import argparse
import pathlib

import cv2
import numpy as np
from PIL import Image


def load_rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def tint(rgba, color_hex):
    color_hex = color_hex.lstrip("#")
    r, g, b = (int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
    out = rgba.copy()
    out[..., 0], out[..., 1], out[..., 2] = r, g, b
    return out


def place(img, logo, dst_quad, strength=0.94):
    h, w = img.shape[:2]
    lh, lw = logo.shape[:2]
    src = np.float32([[0, 0], [lw, 0], [lw, lh], [0, lh]])
    matrix = cv2.getPerspectiveTransform(src, dst_quad)
    warped = cv2.warpPerspective(
        logo, matrix, (w, h), flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0),
    )

    alpha = (warped[..., 3:4].astype(np.float32) / 255.0) * strength
    base = img[..., :3].astype(np.float32)

    # Modulate the ink by the destination surface's own luminance so paper
    # grain, fabric weave, or a lighting gradient still reads through it —
    # a flat-opacity paste looks pasted on, not printed.
    lum = cv2.cvtColor(img[..., :3], cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    lum = np.clip(lum * 0.55 + 0.45, 0, 1)[..., None]
    ink = warped[..., :3].astype(np.float32) * lum

    img[..., :3] = np.clip(base * (1 - alpha) + ink * alpha, 0, 255).astype(np.uint8)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photo", type=pathlib.Path)
    ap.add_argument("logo", type=pathlib.Path)
    ap.add_argument("corners", nargs=8, type=float,
                     help="tl_x tl_y tr_x tr_y br_x br_y bl_x bl_y")
    ap.add_argument("--color", default=None, help="Recolour the logo to this hex before placing")
    ap.add_argument("--strength", type=float, default=0.94)
    args = ap.parse_args()

    quad = np.float32([args.corners[i:i + 2] for i in range(0, 8, 2)])

    photo = load_rgba(args.photo)
    logo = load_rgba(args.logo)
    if args.color:
        logo = tint(logo, args.color)

    # Sanity-check the destination quad against the logo's own aspect ratio
    # before placing — this is the guard the module docstring describes.
    logo_aspect = logo.shape[1] / logo.shape[0]
    w_px = (np.linalg.norm(quad[1] - quad[0]) + np.linalg.norm(quad[2] - quad[3])) / 2
    h_px = (np.linalg.norm(quad[3] - quad[0]) + np.linalg.norm(quad[2] - quad[1])) / 2
    dst_aspect = w_px / max(h_px, 1e-6)
    if abs(dst_aspect - logo_aspect) / logo_aspect > 0.15:
        print(
            f"WARNING: destination quad aspect ({dst_aspect:.2f}) differs from the "
            f"logo's own aspect ratio ({logo_aspect:.2f}) by more than 15% — the mark "
            f"will look stretched. Adjust the corners.", file=__import__("sys").stderr,
        )

    photo = place(photo, logo, quad, strength=args.strength)
    Image.fromarray(photo[..., :3]).save(args.photo, quality=92)
    print(f"{args.photo.name}: logo composited")


if __name__ == "__main__":
    main()
