#!/usr/bin/env python3
"""Structural check on a built EPUB. Catches the mistakes readers reject over.

    verify.py book.epub
"""

import re
import sys
import xml.dom.minidom as minidom
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import parse as parse_mod  # noqa: E402  (path insert must run first)

XML_SUFFIXES = (".xhtml", ".opf", ".ncx", ".xml", ".svg")
TAG_RE = re.compile(r"<[^>]+>")


def scan_residual_damage(body):
    """Run the same signal detectors parse.py uses on flagged prose, but
    against the finished, repaired book.

    Doing this ad hoc after every real conversion is how the gaps in the
    detector itself got found — a fused "futureyou" with no adjacent damage
    to flag the paragraph, an orphaned footnote asterisk, a drop cap the
    layout heuristic missed. Running it here every time means the next gap
    turns up during review instead of after the reader finds it.
    """
    vocab = parse_mod.load_dictionary()
    bigrams = parse_mod.build_bigrams(" ".join(body))
    counts = Counter()
    for para in body:
        para = para.strip()
        if not para:
            continue
        for sig in parse_mod.damage_signals(para):
            counts[sig.split(":")[0]] += 1
        if parse_mod.fused_words(para, vocab, bigrams):
            counts["fused_word"] += 1
        if parse_mod.split_capitals(para, vocab):
            counts["split_capital"] += 1
    return counts


def check(path):
    problems, notes = [], []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()

        # Readers stream the first entry to identify the file. If mimetype is not
        # first and stored uncompressed, many refuse to open the book at all.
        if not names or names[0] != "mimetype":
            problems.append("mimetype is not the first zip entry")
        elif z.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            problems.append("mimetype is compressed (must be stored)")
        elif z.read("mimetype") != b"application/epub+zip":
            problems.append("mimetype content is wrong")

        for required in ("META-INF/container.xml", "OEBPS/content.opf"):
            if required not in names:
                problems.append(f"missing {required}")

        for name in names:
            if name.endswith(XML_SUFFIXES):
                try:
                    minidom.parseString(z.read(name))
                except Exception as exc:
                    problems.append(f"malformed XML in {name}: {str(exc)[:80]}")

        if "OEBPS/content.opf" in names:
            opf = z.read("OEBPS/content.opf").decode("utf-8", "replace")
            hrefs = set(re.findall(r'href="([^"]+)"', opf))
            for href in hrefs:
                if f"OEBPS/{href}" not in names:
                    problems.append(f"manifest lists missing file: {href}")
            for idref in re.findall(r'idref="([^"]+)"', opf):
                if f'id="{idref}"' not in opf:
                    problems.append(f"spine references unknown id: {idref}")
            for field in ("dc:title", "dc:language", "dc:identifier"):
                if f"<{field}" not in opf:
                    problems.append(f"metadata missing {field}")

        chapters = [n for n in names if n.startswith("OEBPS/text/")]
        empty = [n for n in chapters if len(z.read(n)) < 400]
        if empty:
            problems.append(f"{len(empty)} chapter files look empty: {empty[:5]}")

        leftover = [n for n in chapters if re.search(rb"data:image|!\[", z.read(n))]
        if leftover:
            problems.append(f"images survived stripping in {leftover[:5]}")

        recaps = sum(1 for n in chapters if b'class="recap"' in z.read(n))
        notes.append(f"chapters: {len(chapters)}")
        notes.append(f"with recap: {recaps}/{len(chapters)}")
        notes.append(f"nav.xhtml: {'OEBPS/nav.xhtml' in names}")
        notes.append(f"toc.ncx: {'OEBPS/toc.ncx' in names}")
        notes.append(f"size: {Path(path).stat().st_size / 1024:.0f} KB")

        paragraphs = []
        for n in chapters:
            html = z.read(n).decode()
            body_only = html.split("<body>", 1)[-1]
            # Tag names need a boundary after them, or "<li" false-matches the
            # "<link>" stylesheet tag in <head> and swallows everything up to
            # the next real </p> into one block.
            for block in re.findall(
                r"<(?:p|li|blockquote)(?:\s[^>]*)?>(.*?)</(?:p|li|blockquote)>",
                body_only,
                re.S,
            ):
                paragraphs.append(TAG_RE.sub(" ", block).strip())
        signal_counts = scan_residual_damage(paragraphs)
        if signal_counts:
            notes.append(
                "residual damage signals: "
                + ", ".join(f"{k}={v}" for k, v in sorted(signal_counts.items()))
            )
            notes.append(
                "  these survived repair. Some are expected false positives (an "
                "'Option B offers' split_capital, a genuine 'and/or' slash), but "
                "read a few — a repeated signal after repair usually means real damage."
            )
        else:
            notes.append("residual damage signals: none")

    print(f"{path}\n  " + "\n  ".join(notes))
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nOK: structurally valid EPUB")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py book.epub")
    sys.exit(check(sys.argv[1]))
