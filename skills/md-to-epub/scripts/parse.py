#!/usr/bin/env python3
"""Phase 1 analyzer + chapter slicer for md-to-epub.

analyze: source .md -> headings.json, flags.json, meta.json
slice:   source .md + structure.json -> chapters/NNN.txt (one per chapter)

Nothing here makes editorial judgments. It measures the document and reports
signals so a model can decide. Guessing structure mechanically is exactly how
flat single-level markdown dumps get mangled.
"""

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

DICT_PATHS = ["/usr/share/dict/words", "/usr/dict/words"]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^\s*```")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>", re.I)
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

# Tokens OCR reliably invents. Each is a real signal, not a dictionary miss:
# these are valid-looking strings a spellchecker would wave through.
OCR_CONFUSION = re.compile(
    r"\b(Tn|Th|Ln|1n|ln|0f|0n|arid|thc|thet|tbe|bv|hc|ancl|witb|tliat|liave|"
    r"rnay|rnore|frorn|sorne|tirne|carne|ona|ina|ata|toa|isa|asa|fora)\b"
)
# Function-word pairs no English sentence produces, so a word was dropped
# between them. Kept deliberately tight: "latched on to the story" and "added
# to at will" are ordinary English, and flagging those buries the real damage.
MISSING_WORD = re.compile(
    r"\bto\s+at\b|\bof\s+of\b|\bof\s+to\b|\bthe\s+of\b|\bthe\s+to\b|"
    r"\ban?\s+of\b|\bin\s+in\b|\bfor\s+for\b|\bto\s+to\b|\bat\s+at\b",
    re.I,
)
DOUBLED_WORD = re.compile(r"\b(\w{3,})\s+\1\b", re.I)
# Scanners read an italic lowercase L as a slash, giving "/oss aversion" and
# "i//usion of attention".
SLASH_FOR_L = re.compile(r"(?<![\w/:])/[a-z]{2,}|[a-z]/{1,2}[a-z]")
# A bare pipe or bracket standing in for a capital I: "| have borrowed", "] doubt".
PIPE_FOR_I = re.compile(r"(?:^|\s)[|\]]\s+[a-z]", re.M)
# A capital T standing in for "I" at the start of a quoted first-person
# sentence: '"T don't get her"', '"T hope she is happy"'. Scoped to a quote
# mark immediately before it and a pronoun-shaped verb immediately after, so
# it doesn't fire on a real initial like "T. S. Eliot".
QUOTE_T_FOR_I = re.compile(
    r'["‘’“”]T\s+(?:don|won|can|could|should|would|didn|'
    r"isn|wasn|haven|hadn|am|was|have|had|need|want|hope|will|think|feel|"
    r"know|remember)\b"
)
# A capital sheared off its own word: "T he contrast", "K evin has", "B ruce is".
# I and A are excluded because they are real one-letter words. The dictionary
# test in split_capitals() does the actual work of separating damage from the
# option labels these books are full of ("Option B offers", "Group B heard").
SPLIT_CAPITAL = re.compile(r"\b([B-HJ-Z])\s+([a-z]{2,})\b")
DOUBLED_QUOTE = re.compile(r'""|\'\'|""')
BROKEN_HYPHEN = re.compile(r"[a-z]-\s+[a-z]")
DIGIT_IN_WORD = re.compile(r"[a-z]\d[a-z]", re.I)
# A contraction split by a stray space ("you' ll", "It' 11-Get-Worse"). Matching
# any letter after the apostrophe would swallow every closing single quote in
# the book, so only contraction suffixes and digits count.
SPACED_APOSTROPHE = re.compile(r"(?<![Ss])'\s+(?:ll|ve|re|[stdm])\b|'\s+\d", re.I)

# Latin text plus ordinary typographic punctuation and the symbols real books
# use. Anything outside this in an English book is a scanner hallucination.
ALLOWED_EXTRA = set("‘’“”–—…•·°©®™€£¥§¶†‡×÷≈≤≥±½¼¾ ­﻿")


def load_dictionary():
    for path in DICT_PATHS:
        p = Path(path)
        if p.exists():
            with p.open(encoding="utf-8", errors="ignore") as fh:
                return {line.strip().lower() for line in fh if line.strip()}
    return set()


def is_exotic(ch):
    if ch in ALLOWED_EXTRA or ch.isspace():
        return False
    if ord(ch) < 128:
        return False
    # Accented Latin is legitimate in an English book (café, naïve, Zeigarnik).
    return not unicodedata.name(ch, "").startswith("LATIN")


def split_blocks(lines):
    """Yield (kind, start_line, text). kind is heading | fence | para."""
    blocks = []
    buf, buf_start, in_fence = [], 0, False

    def flush():
        if buf:
            text = "\n".join(buf).strip()
            if text:
                blocks.append(("fence" if in_fence else "para", buf_start, text))
            buf.clear()

    for i, raw in enumerate(lines):
        if FENCE_RE.match(raw):
            flush()
            in_fence = not in_fence
            continue
        if not in_fence and HEADING_RE.match(raw):
            flush()
            m = HEADING_RE.match(raw)
            blocks.append(("heading", i, raw))
            continue
        if not raw.strip():
            flush()
            continue
        if not buf:
            buf_start = i
        buf.append(raw)
    flush()
    return blocks


def analyze_headings(lines, blocks):
    heads = [b for b in blocks if b[0] == "heading"]
    records = []
    for n, (_, line_idx, raw) in enumerate(heads):
        m = HEADING_RE.match(raw)
        level, text = len(m.group(1)), m.group(2).strip()
        end = heads[n + 1][1] if n + 1 < len(heads) else len(lines)
        body = [l for l in lines[line_idx + 1 : end] if l.strip()]
        letters = [c for c in text if c.isalpha()]
        records.append(
            {
                "id": n,
                "line": line_idx + 1,
                "level": level,
                "text": text,
                "words": len(text.split()),
                "body_lines": len(body),
                "body_chars": sum(len(l) for l in body),
                "all_caps": bool(letters) and all(c.isupper() for c in letters),
                "ends_with_colon": text.endswith(":"),
                "first_body_line": (body[0][:160] if body else ""),
                "last_body_line": (body[-1][:160] if body else ""),
            }
        )
    return records


SUFFIXES = ("s", "es", "ed", "ing", "ly", "er", "est", "d", "n")


def known(word, vocab):
    """Dictionary lookup that tolerates inflection.

    The system word list holds base forms only, so a raw lookup reports
    "flashed" and "pulled" as unknown and buries every real signal in noise.
    """
    low = word.lower().rstrip("'")
    if low in vocab:
        return True
    if low.endswith("'s") and low[:-2] in vocab:
        return True
    for suf in SUFFIXES:
        if not low.endswith(suf) or len(low) - len(suf) < 3:
            continue
        stem = low[: -len(suf)]
        # walked -> walk, hopped -> hop, carries -> carry, gambles -> gamble
        for candidate in (stem, stem + "e", stem[:-1], stem[:-1] + "y"):
            if candidate in vocab:
                return True
    return False


def build_bigrams(text):
    """Every truly-adjacent (whitespace-only gap) word pair in the document.

    This is what makes fused-word detection precise. "willpower" and
    "girlfriend" are real compounds a dictionary happens to lack, while
    "baserate" and "withdomain" are damage — and the difference is that the
    book itself writes "base rate" and "with domain" correctly elsewhere. The
    document is its own authority on which compounds it actually uses.

    The gap between the two words is required to be whitespace, or a single
    hyphen optionally padded with whitespace — a real space or a real hyphen
    both mean these are genuinely two words used together elsewhere, which is
    what makes their solid (fused) form suspicious. Any other punctuation in
    the gap means the words are not actually adjacent in the way the fused
    candidate implies. Without that distinction, a parenthetical like
    "(anti)fragility" tokenizes as "anti" then "fragility" with only a stray
    ")" between them, which falsely confirms the solid form "antifragility"
    as a real spaced usage — even though it is the book's own coined term,
    used hundreds of times correctly, and that bracketed shorthand is the
    only place anything resembling "anti fragility" appears.
    """
    matches = list(WORD_RE.finditer(text))
    return {
        m1.group().lower() + m2.group().lower()
        for m1, m2 in zip(matches, matches[1:])
        if text[m1.end() : m2.start()].strip() in ("", "-")
    }


# Real short words that a length-only tail check would otherwise reject.
# "futureyou" (head "future", tail "you") went undetected across a whole book
# before this existed — the tail was a real word, just three letters long.
SHORT_TAILS = {
    "a", "i", "us", "we", "he", "it", "to", "of", "in", "on", "by", "or",
    "is", "me", "my", "no", "so", "up", "do", "be", "as", "at", "if", "you",
}


def fused_words(text, vocab, bigrams):
    """Words that lost the space or hyphen between them: "socalled", "froma"."""
    if not vocab:
        return []
    found = []
    for token in WORD_RE.findall(text):
        low = token.lower()
        if len(low) < 5 or not low.isalpha() or not token[0].islower():
            continue
        if known(low, vocab) or low not in bigrams:
            continue
        for i in range(2, len(low)):
            head, tail = low[:i], low[i:]
            if not known(head, vocab):
                continue
            # "socalled" (head "so") needs no head-length floor because the
            # tail alone ("called") is unambiguous. A short tail like "you" is
            # only trustworthy once the head is long enough that the split
            # can't be two other short real words colliding by chance.
            if (len(tail) >= 4 and known(tail, vocab)) or (
                len(head) >= 4 and tail in SHORT_TAILS
            ):
                found.append(f"{token}={head}+{tail}")
                break
    return found


def split_capitals(text, vocab):
    """Capitals sheared off their own word by a drop-cap or ligature glitch.

    "T he contrast effect" is damage; "Option B offers" is not, and both look
    identical to a regex. The tell is the following token: if it stands alone
    as an English word ("B the", "B offers", "X years") the capital is a label,
    whereas "K evin" and "B ruce" leave a fragment that is not a word at all.
    """
    if not vocab:
        return []
    found = []
    for m in SPLIT_CAPITAL.finditer(text):
        letter, tail = m.group(1), m.group(2)
        joined = letter + tail
        # A match at the very start of a paragraph is almost always a drop cap
        # that came out of the PDF as its own glyph, so it needs no further
        # evidence. Mid-sentence matches are usually option labels and are
        # only worth reporting when the remainder is not a word on its own.
        if m.start() == 0:
            found.append(f"start:{m.group(0)}={joined}")
        elif known(joined, vocab) and not known(tail, vocab):
            found.append(f"{m.group(0)}={joined}")
    return found


def damage_signals(text):
    signals = []
    if SLASH_FOR_L.search(text):
        signals.append("slash_for_l")
    if PIPE_FOR_I.search(text):
        signals.append("pipe_for_i")
    if QUOTE_T_FOR_I.search(text):
        signals.append("quote_t_for_i")
    if DOUBLED_QUOTE.search(text):
        signals.append("doubled_quote")
    exotic = sorted({c for c in text if is_exotic(c)})
    if exotic:
        signals.append("exotic_glyph:" + "".join(exotic))
    if OCR_CONFUSION.search(text):
        signals.append("ocr_confusion")
    if MISSING_WORD.search(text):
        signals.append("missing_word")
    if DOUBLED_WORD.search(text):
        signals.append("doubled_word")
    if BROKEN_HYPHEN.search(text):
        signals.append("broken_hyphen")
    if DIGIT_IN_WORD.search(text):
        signals.append("digit_in_word")
    if SPACED_APOSTROPHE.search(text):
        signals.append("spaced_apostrophe")
    return signals


def unknown_words(text, vocab):
    """Lowercase tokens missing from the system dictionary.

    Only lowercase-initial tokens are checked. Capitalized tokens are usually
    proper nouns (Dobelli, Zeigarnik, Munich) which no dictionary contains, and
    counting them would flag every page of a book about named researchers.
    """
    if not vocab:
        return [], 0
    tokens = [t for t in WORD_RE.findall(text) if t[0].islower() and len(t) > 2]
    unknown = [t for t in tokens if t.lower() not in vocab and t.lower().rstrip("'s") not in vocab]
    return unknown, len(tokens)


def normalize_source(src):
    """Fix mechanical extraction artifacts in place, once, before anything else runs.

    Rewriting the file (not just an in-memory copy) matters because build.py
    re-reads the same file by line number later — both stages need to agree on
    what is on each line.
    """
    text = src.read_text(encoding="utf-8")
    original = text

    # Docling and some other PDF-to-markdown converters use a literal tab
    # character everywhere a real layout used word spacing, so a heading comes
    # out as "Chapter\tOne" and body prose is riddled the same way. A tab is
    # never meaningful inside prose, so this is safe unconditionally rather
    # than treating it as a damage signal to repair paragraph by paragraph.
    tab_count = text.count("\t")
    if tab_count:
        text = text.replace("\t", " ")

    # The same converters sometimes hand back pre-escaped HTML entities
    # (`&lt;topic X&gt;`, `Kleiner Perkins Caufield &amp; Byers`) instead of
    # the literal characters. Left alone, build.py's own HTML escaping runs a
    # second time over already-escaped text and the reader sees literal
    # "&amp;lt;" on the page. Unescaping here means build.py's escaping is the
    # only escaping that ever happens.
    entity_count = len(re.findall(r"&(?:lt|gt|amp|quot|#\d+|#x[0-9a-fA-F]+);", text))
    if entity_count:
        text = html.unescape(text)

    # Piracy-site watermarks on a markdown-native source (no PDF step, so
    # frompdf.py's own watermark stripping never runs) show up as a bare
    # markdown link on its own line, sometimes promoted to a heading, and
    # sometimes with the visible text OCR-mangled ("OUDIIO", "QceanofPDFE")
    # while the href stays intact — that href is what makes it identifiable
    # regardless of how garbled the label got.
    lines = text.split("\n")
    link_line_re = re.compile(r"^(?:#{1,6}\s*)?\[.*\]\((https?://[\w.-]+/?)\)\s*$")
    href_counts = Counter()
    for line in lines:
        m = link_line_re.match(line.strip())
        if m:
            href_counts[m.group(1).rstrip("/")] += 1
    watermark_hrefs = {href for href, n in href_counts.items() if n >= 3}
    watermark_count = 0
    if watermark_hrefs:
        for i, line in enumerate(lines):
            m = link_line_re.match(line.strip())
            if m and m.group(1).rstrip("/") in watermark_hrefs:
                lines[i] = ""
                watermark_count += 1
        text = "\n".join(lines)

    if text != original:
        src.write_text(text, encoding="utf-8")
        if tab_count:
            print(f"normalized {tab_count} tab characters to spaces in {src}")
        if entity_count:
            print(f"unescaped {entity_count} pre-escaped HTML entities in {src}")
        if watermark_count:
            print(f"removed {watermark_count} watermark link lines ({', '.join(watermark_hrefs)}) from {src}")
    return tab_count, entity_count, watermark_count


def analyze(args):
    src = Path(args.source)
    normalize_source(src)
    text = src.read_text(encoding="utf-8")
    lines = text.split("\n")
    blocks = split_blocks(lines)
    vocab = load_dictionary()
    bigrams = build_bigrams(text)

    headings = analyze_headings(lines, blocks)

    flags, para_id = [], 0
    for kind, line_idx, block in blocks:
        # Fences hold the mangled original contents blob and images are stripped
        # from the book entirely, so neither is worth a repair token.
        if kind == "fence" or IMAGE_RE.search(block):
            continue
        signals = damage_signals(block)
        unknown, total = unknown_words(block, vocab)
        ratio = len(unknown) / total if total else 0.0
        if total >= args.min_words and ratio >= args.garble_ratio:
            signals.append(f"garbled:{ratio:.2f}")
        fused = fused_words(block, vocab, bigrams)
        if fused:
            signals.append("fused_word")
        caps = split_capitals(block, vocab)
        if caps:
            signals.append("split_capital")
        if signals:
            flags.append(
                {
                    "para_id": para_id,
                    "line": line_idx + 1,
                    "kind": kind,
                    "signals": signals,
                    "unknown_words": unknown[:12],
                    "fused": fused[:10],
                    "split_capitals": caps[:10],
                    "text": block,
                }
            )
        if kind == "para":
            para_id += 1

    paras = [b for b in blocks if b[0] == "para"]
    meta = {
        "source": str(src),
        "total_lines": len(lines),
        "total_chars": len(text),
        "heading_count": len(headings),
        "heading_levels": dict(Counter(h["level"] for h in headings)),
        "paragraph_count": len(paras),
        "flagged_paragraphs": len(flags),
        "flag_ratio": round(len(flags) / len(paras), 4) if paras else 0.0,
        "image_lines": [i + 1 for i, l in enumerate(lines) if IMAGE_RE.search(l)],
        "unbalanced_fences": sum(1 for l in lines if FENCE_RE.match(l)) % 2 == 1,
        "dictionary_loaded": bool(vocab),
        "signal_totals": dict(
            Counter(s.split(":")[0] for f in flags for s in f["signals"])
        ),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "headings.json").write_text(json.dumps(headings, indent=2), encoding="utf-8")
    (out / "flags.json").write_text(json.dumps(flags, indent=2), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))

    if meta["flag_ratio"] > args.warn_ratio:
        print(
            f"\nWARNING: {meta['flag_ratio']:.0%} of paragraphs flagged. That is high "
            f"enough that the detector is probably firing on style, not damage. "
            f"Raise --garble-ratio before spending tokens on repair.",
            file=sys.stderr,
        )


def slice_chapters(args):
    """Write one plain-text file per chapter for downstream summarizers."""
    lines = Path(args.source).read_text(encoding="utf-8").split("\n")
    structure = json.loads(Path(args.structure).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    chapters = [s for s in structure["sections"] if s["role"] in ("chapter", "front", "back")]
    written = []
    for sec in chapters:
        start, end = sec["start_line"] - 1, sec["end_line"]
        body = "\n".join(lines[start:end]).strip()
        name = f"{sec['number'] or 0:03d}-{sec['id']}.txt"
        (out / name).write_text(body, encoding="utf-8")
        written.append({"id": sec["id"], "file": name, "chars": len(body)})
    (out / "index.json").write_text(json.dumps(written, indent=2), encoding="utf-8")
    print(f"wrote {len(written)} chapter files to {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="measure the document")
    a.add_argument("source")
    a.add_argument("--out", default="build")
    a.add_argument("--garble-ratio", type=float, default=0.22)
    a.add_argument("--min-words", type=int, default=12)
    a.add_argument("--warn-ratio", type=float, default=0.35)
    a.set_defaults(func=analyze)

    s = sub.add_parser("slice", help="split into per-chapter text files")
    s.add_argument("source")
    s.add_argument("structure")
    s.add_argument("--out", default="build/chapters")
    s.set_defaults(func=slice_chapters)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
