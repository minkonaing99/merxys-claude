#!/usr/bin/env python3
"""Extract clean markdown from a text-layer PDF.

    frompdf.py book.pdf -o book.from-pdf.md

Use this whenever a PDF of the same book exists alongside an OCR'd markdown
dump. A PDF exported by calibre, InDesign, or Word carries the publisher's own
text layer, so it has none of the scanner damage the markdown does and the
whole repair phase becomes unnecessary. Check `pdffonts` or the Creator field:
if the PDF is a scan of paper, this script gets you nothing and the markdown is
just as good a starting point.

Requires the `pdftotext` binary (poppler). Install with `brew install poppler`.
"""

import argparse
import re
import statistics
import subprocess
import sys
from pathlib import Path

CHAPTER_NUM_RE = re.compile(r"^\s*(\d{1,3})\s*$")
# Some layouts mark a chapter with words instead of a bare page number.
CHAPTER_MARKER_RE = re.compile(
    r"^(CHAPTER\s+\d+|PART\s+[\dIVXLC]+|INTRODUCTION|PROLOGUE|PREFACE|"
    r"FOREWORD|EPILOGUE|CONCLUSION|AFTERWORD)\s*:?\s*$",
    re.I,
)
# Piracy sites stamp every extracted page with their own domain. It repeats
# dozens of times as a standalone line and is never part of the book.
WATERMARK_RE = re.compile(r"^\s*[\w.-]+\.(com|net|org)\s*$", re.I)
# A line that ends a paragraph sits well short of the wrap width. PDF text has
# no blank line between paragraphs, so line length is the only available signal.
SHORT_LINE_SLACK = 12


def extract_text(pdf):
    try:
        out = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        raise SystemExit("pdftotext not found. Install poppler (brew install poppler).")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"pdftotext failed: {exc.stderr.decode()[:200]}")
    return out.stdout.decode("utf-8", "replace")


NAMED_SECTIONS = (
    "Introduction",
    "Epilogue",
    "Prologue",
    "Preface",
    "Foreword",
    "Afterword",
    "Acknowledgments",
    "Acknowledgements",
    "A Note on Sources",
    "About the Author",
    "About the Publisher",
    "Credits",
    "Dedication",
    "Contents",
    "Copyright",
    "Notes",
    "Index",
    "Bibliography",
)


def wrap_width(lines):
    """The column the typesetter wrapped at.

    Deliberately the 75th percentile rather than the max or a high percentile:
    endnote and contents pages use a wider measure than body text, and letting
    them set the width makes every body paragraph look short enough to end.
    """
    lengths = sorted(len(l) for l in lines if len(l) > 40)
    if not lengths:
        return 80
    return lengths[int(len(lengths) * 0.75)]


def mend_drop_caps(lines):
    """Reunite a decorative drop cap with the word it was lifted from.

    Some typesetting renders a drop cap as its own character, so extraction
    sees a paragraph's first letter as a standalone line: "W" then, on the
    next line, "hen I was twenty-six...". This is unambiguous — a lone capital
    immediately before a line starting in lowercase can only be the word it
    was carved out of — so it is repaired here rather than left for the
    damage detector to flag as a suspicious one-letter paragraph.
    """
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if len(line) == 1 and line.isalpha() and line.isupper() and nxt[:1].islower():
            out.append(line + nxt)
            i += 2
            continue
        out.append(lines[i])
        i += 1
    return out


def reflow(lines, width):
    """Join hard-wrapped lines back into paragraphs."""
    paras, buf = [], []

    def flush():
        if buf:
            paras.append(" ".join(b.strip() for b in buf).strip())
            buf.clear()

    for line in lines:
        stripped = line.rstrip()
        if not stripped.strip():
            flush()
            continue
        buf.append(stripped)
        if len(stripped) < width - SHORT_LINE_SLACK:
            flush()
    flush()
    return [p for p in paras if p]


def find_watermark_lines(pages):
    """Domain-stamp lines a piracy site injects on every page.

    A single domain-like line could be a real citation, so this only treats it
    as a watermark once it repeats often enough that coincidence is implausible.
    """
    counts = {}
    for page in pages:
        for line in page.split("\n"):
            stripped = line.strip()
            if WATERMARK_RE.match(stripped):
                counts[stripped] = counts.get(stripped, 0) + 1
    return {text for text, n in counts.items() if n >= 3}


def find_chapters(pages):
    """Locate chapter openings: a page whose first line is a bare number.

    The number is followed by the title (sometimes wrapped over two lines) and
    then the subtitle, which is how this layout marks every chapter.
    """
    starts = {}
    for idx, page in enumerate(pages):
        lines = [l for l in page.split("\n") if l.strip()]
        if not lines:
            continue
        m = CHAPTER_NUM_RE.match(lines[0])
        if m and 1 <= int(m.group(1)) <= 200:
            starts[idx] = int(m.group(1))
    return starts


def find_chapter_markers(pages, watermarks):
    """Locate chapters marked by a word, not a number: "CHAPTER 1", "INTRODUCTION".

    Used when find_chapters() comes back too thin to trust — a numberless
    layout like this one would otherwise read as having no chapters at all.
    """
    starts = {}
    for idx, page in enumerate(pages):
        lines = [l.strip() for l in page.split("\n") if l.strip() and l.strip() not in watermarks]
        if lines and CHAPTER_MARKER_RE.match(lines[0]):
            starts[idx] = lines[0].upper().rstrip(":")
    return starts


def parse_contents_titles(pages, markers, watermarks):
    """Read exact chapter titles from the book's own table of contents.

    A layout that marks chapters by keyword rather than a numbered heading
    tends to run the title straight into the first subsection heading with no
    reliable separator, so guessing the title by line length merges the two.
    The contents page lists each title on its own line right after the same
    marker word, so it settles the question instead of guessing.
    """
    # The listing commonly spans more than one PDF page, so page-by-page
    # scanning misses every title after whichever page break falls in the
    # middle of it. Joining a front-matter window first means the listing is
    # searched as one continuous stream regardless of where it was paginated.
    front = "\n".join(pages[: min(20, len(pages))])
    lines = [l.strip() for l in front.split("\n") if l.strip() and l.strip() not in watermarks]
    labels = set(markers.values())

    try:
        i = next(n for n, l in enumerate(lines) if l.upper() == "CONTENTS")
    except StopIteration:
        return {}

    titles, seen = {}, set()
    while i < len(lines) and len(seen) < len(labels):
        up = lines[i].upper()
        hit = next((lbl for lbl in labels if up == lbl or up.startswith(lbl + " ")), None)
        if hit:
            rest = lines[i][len(hit) :].strip(" :")
            if rest:
                titles[hit] = rest
            elif i + 1 < len(lines):
                titles[hit] = lines[i + 1]
                i += 1
            seen.add(hit)
        i += 1
    return titles


def strip_title_lines(lines, title):
    """Drop the leading lines that spell out an already-known title.

    Whatever is left over — subsection headings, a chapter epigraph — stays in
    the body rather than being guessed at and possibly discarded.
    """
    target = re.sub(r"\s+", "", title).lower()
    acc, i = "", 0
    while i < len(lines) and len(acc) < len(target):
        acc += re.sub(r"\s+", "", lines[i]).lower()
        i += 1
        if acc == target:
            return lines[i:]
    return None


def convert(pdf, out, width_override=None):
    raw = extract_text(pdf)
    pages = raw.split("\f")
    watermarks = find_watermark_lines(pages)
    starts = find_chapters(pages)

    marker_titles = {}
    if len(starts) < 2:
        # A bare page number is one convention among several. When it does not
        # show up at all, fall back to a layout that spells the chapter out —
        # "CHAPTER 1", "INTRODUCTION" — and use the book's own contents page
        # for exact titles, since this layout runs the title straight into the
        # next line with no separator a heuristic could use instead.
        markers = find_chapter_markers(pages, watermarks)
        marker_titles = parse_contents_titles(pages, markers, watermarks)
        starts = markers

    all_lines = [
        l for p in pages for l in p.split("\n") if l.strip() not in watermarks
    ]
    width = width_override or wrap_width(all_lines)

    chunks = []
    for idx, page in enumerate(pages):
        nonblank = [
            l.rstrip()
            for l in page.split("\n")
            if l.strip() and l.strip() not in watermarks
        ]
        if not nonblank:
            continue

        if idx in starts and isinstance(starts[idx], str):
            label = starts[idx]
            title = marker_titles.get(label, "")
            rest = strip_title_lines(nonblank[1:], title) if title else None
            if rest is None:
                # No contents-page title to anchor on, or it didn't match this
                # page's wrapping. Falling back to the marker text itself keeps
                # the chapter from vanishing rather than guessing at prose.
                title = title or label.title()
                rest = nonblank[1:]
            chunks.append(f"## {title}")
            body = rest
        elif idx in starts:
            # A chapter page reads: number, title (sometimes wrapped over two
            # lines), subtitle, blank line, then body. That blank line is the
            # reliable separator - guessing by line length instead swallows the
            # body's first line whenever a chapter opens on something short,
            # such as a quotation, and silently loses that paragraph.
            rawlines = [
                l.rstrip()
                for l in page.split("\n")
                if l.strip() not in watermarks
            ]
            start = rawlines.index(nonblank[0])
            head, cursor = [], start + 1
            while cursor < len(rawlines) and rawlines[cursor].strip():
                head.append(rawlines[cursor].strip())
                cursor += 1
            head_max = int(width * 0.75)
            if not head or any(len(h) >= head_max for h in head):
                head = []
                for line in nonblank[1:3]:
                    if len(line) >= head_max:
                        break
                    head.append(line.strip())
                body = nonblank[1 + len(head) :]
            else:
                body = [l for l in rawlines[cursor:] if l.strip()]
            if len(head) > 1:
                title, subtitle = " ".join(head[:-1]), head[-1]
            else:
                title, subtitle = (head[0] if head else f"Chapter {starts[idx]}"), ""
            chunks.append(f"## {title}")
            if subtitle:
                chunks.append(subtitle)
        elif len(nonblank[0].strip()) < 60 and any(
            n.lower() in nonblank[0].strip().rstrip(":").lower() for n in NAMED_SECTIONS
        ):
            # Substring match, not exact: a bibliography section is as likely
            # to be titled "Selected Bibliography and Recommendations" as
            # plain "Bibliography", and the length cap keeps this from firing
            # on an ordinary sentence that happens to contain one of these
            # words. Casing is preserved rather than normalized, so a
            # structure.json written against an earlier extraction of the same
            # book still matches heading text exactly.
            chunks.append(f"## {nonblank[0].strip().rstrip(':')}")
            body = nonblank[1:]
        else:
            body = nonblank
        chunks.extend(reflow(mend_drop_caps(body), width))

    text = "\n\n".join(chunks) + "\n"
    Path(out).write_text(text, encoding="utf-8")
    print(
        f"{out}\n  pages: {len(pages)}   chapters found: {len(starts)}   "
        f"watermark lines removed: {sum(1 for p in pages for l in p.split(chr(10)) if l.strip() in watermarks)}   "
        f"wrap width: {width}   chars: {len(text)}"
    )
    return starts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--width", type=int, help="override detected wrap width")
    args = ap.parse_args()
    convert(args.pdf, args.out, args.width)


if __name__ == "__main__":
    main()
