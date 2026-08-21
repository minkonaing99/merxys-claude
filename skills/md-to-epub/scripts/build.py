#!/usr/bin/env python3
"""Assemble a clean EPUB from source markdown + structure.json.

Pure standard library. An EPUB is a zip with a fixed layout, so pandoc and
calibre buy nothing here and cost control over the markup.

    build.py book.md build/structure.json -o book.epub \
        --recaps build/recaps.json --repairs build/repairs.jsonl
"""

import argparse
import html
import json
import re
import unicodedata
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>", re.I)
HEADING_RE = re.compile(r"^#{1,6}\s+")
FENCE_RE = re.compile(r"^\s*```")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC_RE = re.compile(r"(?<![\*\w])\*([^*\n]+?)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
# OCR splits words across a line break as "prob-\nlem". Only rejoin when a
# lowercase letter sits on both sides; "self-\nnavigating" would be a real
# hyphen, but so would "Pan-\nAmerican", hence the lowercase requirement.
HYPHEN_SPLIT_RE = re.compile(r"([a-z])-\n([a-z])")
# A footnote reference left dangling once its endnote gets dropped: a single
# asterisk right after a word or closing punctuation, with nothing but space
# or more punctuation on the other side. The lookaround excludes anything
# already bordered by another asterisk, so **bold** markers and mid-word
# emphasis like the censored "A**hole" survive untouched.
FOOTNOTE_MARKER_RE = re.compile(r'(?<=[a-zA-Z0-9.,;:!?"’)\]])\*(?=[\s.,;:!?"’)\]]|$)')

CSS = """/* Structure only. No font-family, font-size, or color is set, so the
   reader's own typeface, text size, margins, and dark mode keep working.
   Overriding those is the fastest way to make an ebook worse on real devices. */
body { margin: 0 5%; line-height: 1.6; }
h1 { line-height: 1.25; margin: 2em 0 0; text-align: left; }
p.subtitle { margin: 0.4em 0 2em; font-style: italic; opacity: 0.75; }
p { margin: 0; text-indent: 1.3em; text-align: justify; }
p.first { text-indent: 0; margin-top: 1.2em; }
blockquote { margin: 1.2em 2em; font-style: italic; }
ul, ol { margin: 1.2em 0; }
hr { border: 0; border-top: 1px solid currentColor; opacity: 0.25; margin: 2em 20%; }

/* currentColor keeps the box visible in both light and dark themes without
   pinning a colour the reader did not choose. */
aside.recap {
  margin: 2.5em 0 1em; padding: 0.9em 1.1em;
  border: 1px solid currentColor; border-radius: 3px;
}
aside.recap h2 {
  margin: 0 0 0.5em; font-size: 0.8em; font-weight: bold;
  letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.65;
}
aside.recap p { text-indent: 0; margin: 0; text-align: left; }
nav#toc ol { list-style: none; padding-left: 0; }
nav#toc li { margin: 0.55em 0; }
nav#toc .bias { display: block; opacity: 0.7; font-style: italic; }
"""

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

COVER_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2400"
     viewBox="0 0 1600 2400" preserveAspectRatio="xMidYMid meet">
  <rect width="1600" height="2400" fill="#111417"/>
  <rect x="110" y="110" width="1380" height="2180" fill="none"
        stroke="#8a8f96" stroke-width="3"/>
  <text x="800" y="900" text-anchor="middle" fill="#f4f4f2"
        font-family="Georgia, 'Times New Roman', serif" font-size="{title_size}">
{title_lines}  </text>
  <line x1="620" y1="1120" x2="980" y2="1120" stroke="#8a8f96" stroke-width="3"/>
  <text x="800" y="1270" text-anchor="middle" fill="#c9ccd1"
        font-family="Georgia, 'Times New Roman', serif" font-size="64"
        letter-spacing="6">{author}</text>
</svg>
"""

XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="../style.css"/>
</head>
<body>
{body}</body>
</html>
"""


def esc(text):
    return html.escape(text, quote=False)


def slugify(text, fallback="section"):
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", norm.lower()).strip("-")
    return slug[:48] or fallback


def clean_lines(raw_lines):
    """Mechanical cleanup only. Nothing here changes a word."""
    text = "\n".join(raw_lines)
    text = IMAGE_RE.sub("", text)
    text = HYPHEN_SPLIT_RE.sub(r"\1\2", text)
    text = FOOTNOTE_MARKER_RE.sub("", text)
    text = text.replace("­", "").replace("﻿", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    kept, in_fence = [], False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        kept.append(line)
    return kept


def inline(text):
    text = esc(text)
    text = LINK_RE.sub(r"\1", text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    return text.strip()


def blocks_to_xhtml(lines):
    """Convert a chapter's cleaned lines into XHTML body markup."""
    out, buf, mode = [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        joined = " ".join(b.strip() for b in buf).strip()
        if mode == "quote":
            out.append(f"  <blockquote><p>{inline(joined)}</p></blockquote>")
        elif mode == "list":
            items = "".join(f"<li>{inline(i)}</li>" for i in buf if i.strip())
            out.append(f"  <ul>{items}</ul>")
        elif joined:
            cls = ' class="first"' if not any(o.startswith("  <p") for o in out) else ""
            out.append(f"  <p{cls}>{inline(joined)}</p>")
        buf, mode = [], None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if HEADING_RE.match(stripped):
            # structure.json normally excludes the heading line that opens a
            # chapter, so this only fires on a heading some other section of
            # the book demoted into the body — a book with several named
            # subsections per chapter (see "Chapters with internal subsection
            # headings" in SKILL.md), not a fresh chapter that was missed.
            # Dropping it silently would delete real title text; rendering it
            # bold keeps the section break without promoting it to a real
            # <h*> the reader's table of contents would pick up.
            flush()
            text = HEADING_RE.sub("", stripped).strip()
            if text:
                out.append(f"  <p><strong>{inline(text)}</strong></p>")
            continue
        if stripped in ("---", "***", "* * *"):
            # A visible <hr/> reads fine for a book with two or three of these,
            # but essay-collection books can carry dozens of scene breaks
            # (see "Repaired divider corruption" in SKILL.md), and a solid bar
            # every paragraph or two reads as visual clutter rather than
            # structure. A plain paragraph gap carries the same break without
            # the noise, so that is the default; render <hr/> explicitly only
            # if the book's own layout calls for a rule this dense.
            flush()
            continue
        if stripped.startswith(">"):
            if mode != "quote":
                flush()
                mode = "quote"
            buf.append(stripped.lstrip("> "))
            continue
        if re.match(r"^[-*+]\s+", stripped):
            if mode != "list":
                flush()
                mode = "list"
            buf.append(re.sub(r"^[-*+]\s+", "", stripped))
            continue
        if mode in ("quote", "list"):
            flush()
        mode = mode or "para"
        buf.append(stripped)
    flush()
    return "\n".join(out) + "\n"


def apply_repairs(lines, repairs_path):
    """Replace repaired text in place, reporting anything that no longer matches."""
    if not repairs_path:
        return lines, 0
    text = "\n".join(lines)
    applied, missed = 0, []
    for line in Path(repairs_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        before, after = rec.get("before", ""), rec.get("after", "")
        if not before or before == after:
            continue
        if before in text:
            text = text.replace(before, after, 1)
            applied += 1
        else:
            missed.append(rec.get("line", "?"))
    if missed:
        print(f"  warning: {len(missed)} repairs did not match source (lines {missed[:8]})")
    return text.split("\n"), applied


def chapter_xhtml(sec, lines, recap, lang):
    title = sec["title"]
    heading = f"{sec['number']}. {title}" if sec.get("number") else title
    body = [f"  <h1>{esc(heading)}</h1>"]
    if sec.get("subtitle"):
        body.append(f'  <p class="subtitle">{esc(sec["subtitle"])}</p>')
    body.append(blocks_to_xhtml(lines))
    if recap:
        body.append(
            '  <aside class="recap" epub:type="sidebar">\n'
            "    <h2>Recap</h2>\n"
            f"    <p>{inline(recap)}</p>\n"
            "  </aside>"
        )
    doc = XHTML.format(lang=lang, title=esc(heading), body="\n".join(body) + "\n")
    return doc.replace(
        '<html xmlns="http://www.w3.org/1999/xhtml"',
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"',
    )


def build_nav(chapters, lang, title):
    items = []
    for sec in chapters:
        label = f"{sec['number']}. {sec['title']}" if sec.get("number") else sec["title"]
        bias = f'<span class="bias">{esc(sec["subtitle"])}</span>' if sec.get("subtitle") else ""
        items.append(f'      <li><a href="text/{sec["file"]}">{esc(label)}{bias}</a></li>')
    body = (
        '  <nav epub:type="toc" id="toc">\n    <h1>Contents</h1>\n    <ol>\n'
        + "\n".join(items)
        + "\n    </ol>\n  </nav>\n"
    )
    doc = XHTML.format(lang=lang, title="Contents", body=body)
    return doc.replace('href="../style.css"', 'href="style.css"').replace(
        '<html xmlns="http://www.w3.org/1999/xhtml"',
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"',
    )


def build_ncx(chapters, book_id, title):
    points = []
    for n, sec in enumerate(chapters, 1):
        label = f"{sec['number']}. {sec['title']}" if sec.get("number") else sec["title"]
        points.append(
            f'    <navPoint id="np{n}" playOrder="{n}">\n'
            f"      <navLabel><text>{esc(label)}</text></navLabel>\n"
            f'      <content src="text/{sec["file"]}"/>\n'
            f"    </navPoint>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
        f'  <head><meta name="dtb:uid" content="{book_id}"/></head>\n'
        f"  <docTitle><text>{esc(title)}</text></docTitle>\n"
        "  <navMap>\n" + "\n".join(points) + "\n  </navMap>\n</ncx>\n"
    )


def build_opf(meta, chapters, book_id):
    items = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '    <item id="css" href="style.css" media-type="text/css"/>',
        '    <item id="cover-img" href="cover.svg" media-type="image/svg+xml" properties="cover-image"/>',
        '    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['    <itemref idref="cover"/>', '    <itemref idref="nav"/>']
    for n, sec in enumerate(chapters, 1):
        items.append(
            f'    <item id="c{n}" href="text/{sec["file"]}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'    <itemref idref="c{n}"/>')
    creators = "".join(
        f"    <dc:creator>{esc(a)}</dc:creator>\n" for a in meta.get("creators", [])
    )
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'    <dc:identifier id="bookid">urn:uuid:{book_id}</dc:identifier>\n'
        f"    <dc:title>{esc(meta['title'])}</dc:title>\n"
        f"{creators}"
        f"    <dc:language>{meta.get('language', 'en')}</dc:language>\n"
        f'    <meta property="dcterms:modified">{stamp}</meta>\n'
        "  </metadata>\n  <manifest>\n" + "\n".join(items) + "\n  </manifest>\n"
        '  <spine toc="ncx">\n' + "\n".join(spine) + "\n  </spine>\n</package>\n"
    )


def build_cover(title, author, lang):
    words, lines, cur = title.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 18 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    size = 150 if max(len(l) for l in lines) <= 14 else 120
    start = -(len(lines) - 1) * size * 0.6
    spans = "".join(
        f'    <tspan x="800" dy="{size * 1.2 if i else start:.0f}">{esc(l)}</tspan>\n'
        for i, l in enumerate(lines)
    )
    svg = COVER_SVG.format(title_size=size, title_lines=spans, author=esc(author))
    page = XHTML.format(
        lang=lang,
        title="Cover",
        body='  <div style="text-align:center;margin:0;padding:0">'
        '<img src="cover.svg" alt="Cover" style="max-width:100%"/></div>\n',
    )
    return svg, page.replace('href="../style.css"', 'href="style.css"')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("structure")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--recaps")
    ap.add_argument("--repairs")
    args = ap.parse_args()

    src_lines = Path(args.source).read_text(encoding="utf-8").split("\n")
    struct = json.loads(Path(args.structure).read_text(encoding="utf-8"))
    recaps = json.loads(Path(args.recaps).read_text(encoding="utf-8")) if args.recaps else {}

    src_lines, repaired = apply_repairs(src_lines, args.repairs)
    lang = struct.get("language", "en")
    title = struct.get("title", Path(args.source).stem)
    creators = struct.get("creators") or ([struct["author"]] if struct.get("author") else [])

    chapters = [s for s in struct["sections"] if s.get("role") == "chapter"]
    if not chapters:
        raise SystemExit("structure.json contains no sections with role 'chapter'")
    for n, sec in enumerate(chapters, 1):
        sec["file"] = f"{n:03d}-{slugify(sec['title'], f'ch{n}')}.xhtml"

    book_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"md-to-epub:{title}:{creators}"))
    svg, cover_page = build_cover(title, ", ".join(creators) or "Unknown", lang)
    meta = {"title": title, "creators": creators, "language": lang}

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        # The mimetype entry must be first and stored uncompressed, or readers
        # reject the file outright.
        z.writestr(
            zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED
        )
        z.writestr("META-INF/container.xml", CONTAINER)
        z.writestr("OEBPS/style.css", CSS)
        z.writestr("OEBPS/cover.svg", svg)
        z.writestr("OEBPS/cover.xhtml", cover_page)
        z.writestr("OEBPS/nav.xhtml", build_nav(chapters, lang, title))
        z.writestr("OEBPS/toc.ncx", build_ncx(chapters, book_id, title))
        z.writestr("OEBPS/content.opf", build_opf(meta, chapters, book_id))
        for sec in chapters:
            body = clean_lines(src_lines[sec["start_line"] - 1 : sec["end_line"]])
            recap = recaps.get(sec["id"], "")
            z.writestr(f"OEBPS/text/{sec['file']}", chapter_xhtml(sec, body, recap, lang))

    with_recap = sum(1 for s in chapters if recaps.get(s["id"]))
    dropped = len(struct["sections"]) - len(chapters)
    print(
        f"{out}  ({out.stat().st_size / 1024:.0f} KB)\n"
        f"  chapters: {len(chapters)}   dropped sections: {dropped}\n"
        f"  recaps:   {with_recap}/{len(chapters)}   repairs applied: {repaired}"
    )


if __name__ == "__main__":
    main()
