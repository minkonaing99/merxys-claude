#!/usr/bin/env python3
"""Merge per-batch subagent output and check it against structure.json.

    merge.py recaps  build/recaps-*.json  -o build/recaps.json  -s build/structure.json
    merge.py repairs build/repairs-*.jsonl -o build/repairs.jsonl

Batches finish independently and any one of them can come back short, so the
point of this is the reconciliation, not the concatenation.
"""

import argparse
import json
import sys
from pathlib import Path


def merge_recaps(paths, out, structure):
    merged, clashes = {}, []
    for p in paths:
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  SKIPPED {p}: invalid JSON ({exc})")
            continue
        for key, value in data.items():
            if key in merged and merged[key] != value:
                clashes.append(key)
            merged[key] = value
    Path(out).write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

    problems = []
    if clashes:
        problems.append(f"{len(clashes)} ids written twice with different text: {clashes[:5]}")
    if structure:
        struct = json.loads(Path(structure).read_text(encoding="utf-8"))
        wanted = [s["id"] for s in struct["sections"] if s.get("role") == "chapter"]
        missing = [i for i in wanted if i not in merged]
        extra = [i for i in merged if i not in wanted]
        print(f"{out}: {len(merged)} recaps for {len(wanted)} chapters")
        if missing:
            problems.append(f"{len(missing)} chapters have no recap: {missing[:8]}")
        if extra:
            problems.append(f"{len(extra)} recaps match no chapter id: {extra[:8]}")
        short = [k for k, v in merged.items() if len(v.split()) < 15]
        if short:
            problems.append(f"{len(short)} recaps under 15 words, likely truncated: {short[:8]}")
    else:
        print(f"{out}: {len(merged)} recaps")
    return problems


def merge_repairs(paths, out):
    lines, seen, problems = [], set(), []
    for p in paths:
        for n, raw in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                problems.append(f"{p}:{n} is not valid JSON")
                continue
            if not rec.get("before") or "after" not in rec:
                problems.append(f"{p}:{n} missing before/after")
                continue
            if rec["before"] == rec["after"]:
                continue
            if rec["before"] in seen:
                continue
            seen.add(rec["before"])
            lines.append(json.dumps(rec, ensure_ascii=False))
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out}: {len(lines)} repairs")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("kind", choices=["recaps", "repairs"])
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("-s", "--structure")
    args = ap.parse_args()

    if args.kind == "recaps":
        problems = merge_recaps(args.inputs, args.out, args.structure)
    else:
        problems = merge_repairs(args.inputs, args.out)

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(f"  - {p}")
        print("\nRerun the affected batches before building.")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
