"""Render a brand-book HTML file to PDF via headless Chrome, verify the page
count came out right, and check every page actually painted content.

Headless Chrome is the export path because it's the one local engine that
honours container queries, web fonts and CSS gradients together —
weasyprint and wkhtmltopdf do not. See references/page-system.md for the
print stylesheet this expects the HTML to already have.

    python build_pdf.py <source.html> <output.pdf> [--expect-pages N]

A page-count mismatch against --expect-pages almost always means a page
overflowed its 16:9 box and split into two — that's the signal to look at,
not a hard failure to suppress.

REAL BUG THIS SCRIPT GUARDS AGAINST, found the hard way: page count matching
is not enough. In a real ~25-page book, headless Chrome's single-process
print-to-pdf silently failed to paint one page's content — headline and
folio present, body text and a real, valid image both just missing — while
every other page, including ones reusing the exact same image, rendered
correctly. It reproduced across repeated full-document exports and even a
same-adjacency two-page export, but rendering that one page alone always
came out fine. That combination (fine alone, broken in a large batch, not
tied to a specific page or image) points to the print pipeline itself
dropping a paint under load, not a markup bug — --virtual-time-budget and
--run-all-compositor-stages-before-draw did not fix it.

The reliable fix was to render every page as its own single-page PDF (each
export gets the "renders fine alone" treatment) and merge them in order —
--split-render below does exactly that, and is worth reaching for whenever
--verify-content flags a suspect page. It's slower (one Chrome launch per
page) but every page individually verified real before this script shipped
a result built that way.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

# A real page's extracted text is almost always well above this; the spine
# footer + headline + folio alone (a page whose body silently failed to
# paint) lands around 60-90 characters. Divider/cover pages are exempted by
# position, not length, since they're legitimately this short on purpose.
MIN_TEXT_CHARS = 150


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if pathlib.Path(candidate).exists():
            return candidate
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    sys.exit("No Chrome or Edge binary found — install one or edit CHROME_CANDIDATES.")


def print_to_pdf(chrome, html_path, pdf_path, budget_ms, extra_flags=()):
    subprocess.run(
        [
            chrome, "--headless", "--disable-gpu", "--window-size=1920,1080",
            "--no-pdf-header-footer", f"--virtual-time-budget={budget_ms}",
            *extra_flags,
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True, capture_output=True,
    )


def verify_content(pdf_path, exempt_indices=()):
    """Return a list of (page_index, char_count) for pages that look like
    they silently failed to paint their body content."""
    import pymupdf
    doc = pymupdf.open(pdf_path)
    suspects = []
    for i in range(doc.page_count):
        if i in exempt_indices:
            continue
        chars = len(doc[i].get_text())
        if chars < MIN_TEXT_CHARS:
            suspects.append((i, chars))
    return suspects


def split_render_merge(source, output, budget_ms, chrome):
    """Render each top-level page section as its own single-page PDF, then
    merge in order — the reliable fix documented in the module docstring."""
    import pymupdf

    html = source.read_text(encoding="utf-8")
    doc_open = html.index('<div class="doc">') + len('<div class="doc">')
    head, body, tail = html[:doc_open], html[doc_open:], "\n</div>"

    # Split on the numbered HTML comments this skill's page template uses
    # (e.g. "<!-- 03 WHO WE ARE -->") — one marker per top-level page.
    markers = [m.start() for m in re.finditer(r"<!--\s*\d", body)]
    if not markers:
        sys.exit(
            "split-render needs numbered page markers (<!-- 01 ... -->, "
            "<!-- 02 ... -->, ...) in the source HTML to split on."
        )
    markers.append(len(body))
    sections = [body[markers[i]:markers[i + 1]] for i in range(len(markers) - 1)]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        merged = pymupdf.open()
        for i, section in enumerate(sections):
            # Relative asset paths (src="assets/...") resolve against the
            # split file's own directory — rewrite them to an absolute path
            # back to the source document's directory, or every image
            # silently 404s (found this the hard way: the first split-render
            # attempt "fixed" the missing-body-text bug and broke every
            # image on the page it had just fixed).
            fixed = re.sub(
                r'src="assets/', f'src="{source.parent.as_posix()}/assets/', section
            )
            page_html = tmp / f"p{i:02d}.html"
            page_pdf = tmp / f"p{i:02d}.pdf"
            page_html.write_text(head + fixed + tail, encoding="utf-8")
            print_to_pdf(chrome, page_html, page_pdf, budget_ms)
            merged.insert_pdf(pymupdf.open(page_pdf))
        merged.save(output)
    return merged.page_count


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("source", type=pathlib.Path, help="Source HTML file")
    ap.add_argument("output", type=pathlib.Path, help="Output PDF path")
    ap.add_argument("--expect-pages", type=int, default=None,
                     help="Fail if the exported PDF doesn't have exactly this many pages")
    ap.add_argument("--budget-ms", type=int, default=20000,
                     help="--virtual-time-budget for Chrome (raise if fonts/images load slowly)")
    ap.add_argument("--exempt", type=int, nargs="*", default=[],
                     help="0-indexed page numbers to skip the content-length check on "
                          "(cover, dividers — pages that are short on purpose)")
    ap.add_argument("--split-render", action="store_true",
                     help="Render each page as its own PDF and merge — slower, but "
                          "sidesteps the full-document paint-drop bug in this script's "
                          "docstring. Use this directly if you already know a page is "
                          "flaky, or re-run with it after --expect-pages or the content "
                          "check flags something.")
    args = ap.parse_args()

    if not args.source.exists():
        sys.exit(f"Missing source document: {args.source}")

    chrome = find_chrome()

    if args.split_render:
        pages = split_render_merge(args.source, args.output, args.budget_ms, chrome)
    else:
        print_to_pdf(chrome, args.source, args.output, args.budget_ms)
        try:
            import pymupdf
            pages = pymupdf.open(args.output).page_count
        except ImportError:
            print(f"Wrote {args.output.name} (install pymupdf to verify page count and content).")
            return

    print(f"Wrote {args.output.name} — {pages} pages.")

    if args.expect_pages is not None and pages != args.expect_pages:
        sys.exit(
            f"Expected {args.expect_pages} pages, got {pages}: a page likely "
            f"overflowed its 16:9 box and split. Check the HTML, don't just "
            f"raise --expect-pages."
        )

    suspects = verify_content(args.output, exempt_indices=set(args.exempt))
    if suspects:
        listing = ", ".join(f"page {i} ({n} chars)" for i, n in suspects)
        print(
            f"WARNING: {len(suspects)} page(s) look like they silently failed to "
            f"paint body content: {listing}. If these aren't meant to be this "
            f"short (cover/divider — pass their index to --exempt if so), "
            f"re-run with --split-render.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
