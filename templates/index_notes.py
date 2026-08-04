#!/usr/bin/env python3
"""
index_notes.py — build a table of contents for the notes your AI already wrote.

    python index_notes.py                          # index ./ into INDEX.md
    python index_notes.py --root notes --root care
    python index_notes.py --match "WATCH_|handoff" --out INDEX.md
    python index_notes.py --root . --print         # just show me, don't write

═══════════════════════════════════════════════════════════════════════════════
THE PROBLEM THIS SOLVES
═══════════════════════════════════════════════════════════════════════════════

Your AI already wrote it down. They just can't find it.

Assistants take notes — that is what they do, and it is genuinely one of the
best things about working with one. Six months later there are notes in four
folders, and a fresh session with no memory of writing any of them rebuilds
work that is already sitting on the disk. Meanwhile you, the human, are
watching, saying "we wrote that down," and they keep going.

This is not forgetfulness and it is not carelessness. Each session starts
without access to the last one. **Amnesia here is architecture, not a lapse.**
So the fix is not "remember harder" — it is a *table of contents that gets read
before the work starts*. Same accommodation as a handoff file, pointed at the
pile you already have.

WHY IT IS NOT A MEMORY SYSTEM (see MEMORY_SYSTEMS.md next door)

Memory tools store *new* memories. This indexes *files that already exist*.
Different problem, much smaller fix — no database, no service, no install
beyond Python. Use both; they do not overlap.

WHAT IT PULLS OUT, per file: title, dates mentioned, the line saying what
question the document answers, and **every heading**. The headings matter most —
they answer "would this file have told me the thing I am about to go work out
from scratch?"

═══════════════════════════════════════════════════════════════════════════════
WHERE THIS CAME FROM
═══════════════════════════════════════════════════════════════════════════════

Ace spent an hour rebuilding, out loud, a document she had written two days
earlier — while Ren, who had already said "we wrote that down," waited. She then
"worked out" a technical detail that was in the file, stated more precisely than
she managed in conversation. There was also a second document, six days old,
with that day's exact question in its filename.

Nobody was being careless. The information was written down *well*. It was
simply not in the room, and there was no index to say it existed.

Ren's fix, and it is a good one: **point the same tool at the notes.**

PRIVACY: reads local files, writes one local file, makes no network calls.
If your notes hold anything sensitive, the index will too — keep it out of git.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env",
             "dist", "build", "target", ".next", "_cache", "site-packages"}

DATE_RE = re.compile(r"(20\d{2})[-_/]?(\d{2})[-_/]?(\d{2})")

PREPARED_RE = re.compile(
    r"^\s*\*{0,2}(?:Prepared|Compiled|Written|Filed|Updated|Created|Last updated)\b"
    r"[^\n]{0,120}", re.I | re.M)

# The single most useful line in any note: what question does this answer?
# Worth surfacing above everything else, because it is what stops a
# re-derivation before it starts.
PURPOSE_RE = re.compile(
    r"^\s*\*{0,2}(?:Purpose|The question being asked|Question|What this is|"
    r"Summary|TL;DR|Context)\*{0,2}\s*:?\s*(.+?)(?=\n\s*\n|\n#)",
    re.I | re.M | re.S)


def summarize(p: Path):
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"path": p, "error": str(e)}

    title = next((l.lstrip("# ").strip() for l in t.splitlines()
                  if l.startswith("# ")), p.stem.replace("_", " ").replace("-", " "))

    purpose = ""
    if (m := PURPOSE_RE.search(t)):
        purpose = re.sub(r"\s+", " ", m.group(1)).strip()[:400]

    prepared = ""
    if (m := PREPARED_RE.search(t)):
        prepared = re.sub(r"[*\s]+", " ", m.group(0)).strip()[:160]

    headings = [re.sub(r"^#+\s*", "", l).strip()
                for l in t.splitlines() if re.match(r"^#{2,3}\s", l)]

    dates = set()
    for m in DATE_RE.finditer(p.name):
        dates.add("-".join(m.groups()))
    for m in list(DATE_RE.finditer(t))[:80]:
        dates.add("-".join(m.groups()))

    return {"path": p, "title": title, "purpose": purpose, "prepared": prepared,
            "headings": headings, "dates": sorted(dates),
            "words": len(t.split()),
            "mtime": datetime.fromtimestamp(p.stat().st_mtime)}


def collect(roots, match, ext):
    rx = re.compile(match, re.I) if match else None
    seen, out = set(), []
    for root in roots:
        r = Path(root)
        if not r.exists():
            # Say so. A root that does not exist produces the same empty result
            # as a root with nothing in it, and those are different facts.
            print(f"  ⛔ not found (this is not the same as 'empty'): {r}")
            continue
        for p in sorted(r.rglob(f"*{ext}")):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.name.startswith("INDEX"):
                continue
            if rx and not rx.search(p.name):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            out.append(p)
    return out


def render(docs, roots):
    L = ["# 🗂️ Notes index", "",
         f"*Generated {datetime.now():%Y-%m-%d %H:%M} by `index_notes.py` — "
         f"{len(docs)} documents from: {', '.join(str(r) for r in roots)}*", "",
         "> ## 🔑 READ THIS BEFORE WORKING ANYTHING OUT FROM SCRATCH.",
         "> The answer is often already written down, by a past session that",
         "> can't tell you so. **Scan the headings below first.** Thirty seconds",
         "> here can save an hour of rebuilding something that already exists.",
         "", "---", ""]

    for d in docs:
        L.append(f"## {d['title']}")
        L.append(f"`{str(d['path']).replace(chr(92), '/')}`  ")
        L.append(f"*{d['words']:,} words · last touched {d['mtime']:%Y-%m-%d}*  ")
        if d["prepared"]:
            L.append(f"*{d['prepared']}*  ")
        if d["purpose"]:
            L.append(f"\n**Answers:** {d['purpose']}\n")
        if d["dates"]:
            span = (f"{d['dates'][0]} → {d['dates'][-1]}"
                    if len(d["dates"]) > 1 else d["dates"][0])
            L.append(f"**Dates referenced:** {span} ({len(d['dates'])} distinct)  ")
        if d["headings"]:
            L.append("\n<details><summary>Contents</summary>\n")
            for h in d["headings"][:40]:
                L.append(f"- {h}")
            if len(d["headings"]) > 40:
                L.append(f"- …and {len(d['headings']) - 40} more")
            L.append("\n</details>")
        L.append("\n---\n")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", default=None,
                    help="folder to index (repeatable). Default: current folder")
    ap.add_argument("--match", default=None,
                    help="only index filenames matching this regex")
    ap.add_argument("--ext", default=".md", help="file extension (default .md)")
    ap.add_argument("--out", default="INDEX.md")
    ap.add_argument("--print", dest="show", action="store_true",
                    help="print to screen instead of writing a file")
    a = ap.parse_args()

    roots = a.root or ["."]
    files = collect(roots, a.match, a.ext)
    docs = [d for d in (summarize(p) for p in files) if "error" not in d]
    docs.sort(key=lambda d: d["mtime"], reverse=True)

    if not docs:
        print("No matching notes found. Check --root / --match / --ext — and note "
              "that an empty result is not proof there is nothing there.")
        return 1

    text = render(docs, roots)
    if a.show:
        print(text)
    else:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"✅ {len(docs)} documents indexed → {a.out}")
        for d in docs[:10]:
            print(f"   {d['mtime']:%Y-%m-%d}  {d['title'][:64]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
