#!/usr/bin/env python3
"""check-xrefs.py — find broken cross-references in AsciiDoc documents.

    check-xrefs.py <file.adoc | directory> [...]
    check-xrefs.py --self-test

Exit 0 = clean, 1 = findings, 2 = usage error or asciidoctor missing.

WHY THIS EXISTS
---------------
Asciidoctor does not validate cross-references. An unresolved `<<bogus>>`
produces no warning, no error, and exit code 0 — with `-v`, with
`--failure-level=WARN`, with anything. It renders as an ordinary-looking link
that only fails when a human clicks it. There is no source-level check to lean
on, so this script renders the documents and verifies every reference against
the ids that actually ended up in the output.

Two weaker approaches were tried first and both silently passed while real
breakage sat in the tree:

* trusting `asciidoctor --failure-level=WARN` — it reports nothing at all;
* looking for refs that render as the literal text `[id]` — that only catches
  refs written WITHOUT link text, and it false-positives on valid references to
  untitled blocks.

Checking id existence in the rendered HTML is the approach that works.

WHAT IT CATCHES
---------------
* `<<id>>` / `xref:doc.adoc#id[]` where the anchor does not exist (broken).
* `link:other.adoc[]` — renders as a raw `.adoc` href, which downloads the
  source instead of opening the page; `xref:` is what rewrites to `.html`.
* `xref:doc.adoc[]` with no link text — renders as a bare filename.
* `<<id>>` pointing at an untitled block — resolves, but renders as `[id]`.

For every broken anchor it also diagnoses WHY, because the usual causes are
anchors that silently failed to register:

* `[[a]]` and `[[b]]` on consecutive lines — only the LAST one registers.
* `[[a]]` BETWEEN two list items — does not attach; use an inline anchor.
  (Above the FIRST item it is fine: it attaches to the list.)
* `<<Some Block Title>>` — a `.Block Title` is not a cross-reference target;
  only section titles and explicit ids are.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ID_RE = re.compile(r'\sid="([^"]+)"')
LINK_RE = re.compile(r'<a href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
ANCHOR_DEF_RE = re.compile(r"^\s*(?:\[\[([^\]]+)\]\]|\[#([^\],]+)[^\]]*\])\s*$")
SECTION_RE = re.compile(r"^=+ \S")
LIST_ITEM_RE = re.compile(r"^\s*([*.-]+|\w+\.)\s+\S")


class Finding:
    def __init__(self, doc: str, severity: str, message: str, hint: str = "") -> None:
        self.doc, self.severity, self.message, self.hint = doc, severity, message, hint

    def render(self) -> str:
        out = f"  [{self.severity}] {self.doc}: {self.message}"
        if self.hint:
            out += f"\n           {self.hint}"
        return out


def render_all(docs: list[Path], outdir: Path) -> dict[str, Path]:
    """Render each .adoc to HTML. Returns {stem: html_path}."""
    html: dict[str, Path] = {}
    for doc in docs:
        target = outdir / (doc.stem + ".html")
        proc = subprocess.run(
            ["asciidoctor", "-o", str(target), str(doc)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print(f"  [BROKEN] {doc.name}: asciidoctor failed\n           "
                  f"{proc.stderr.strip().splitlines()[:1]}")
        if target.exists():
            html[doc.stem] = target
    return html


def diagnose(anchor: str, sources: dict[str, list[str]]) -> str:
    """Explain why an anchor that looks defined did not register."""
    if " " in anchor:
        return ("looks like a natural cross-reference to a block title; a `.Block Title` "
                "is not a target — add an explicit `[[id]]` above the block and use it")
    for name, lines in sources.items():
        for i, line in enumerate(lines):
            m = ANCHOR_DEF_RE.match(line)
            if not m or (m.group(1) or m.group(2)) != anchor:
                continue
            where = f"{name}:{i + 1}"
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            prv = lines[i - 1] if i else ""
            if ANCHOR_DEF_RE.match(nxt):
                return (f"defined at {where}, but the anchor on the NEXT line wins — "
                        f"consecutive `[[..]]` anchors: only the last registers")
            if ANCHOR_DEF_RE.match(prv):
                return (f"defined at {where} right after another anchor — only the last "
                        f"of consecutive `[[..]]` anchors registers")
            # An anchor above the FIRST item attaches to the list and registers
            # fine; one BETWEEN items sits inside the list flow and is dropped.
            # "Between" cannot be judged from the previous LINE alone: in
            # ventilated prose the line before is wrapped item text, not a
            # marker. Walk back over the contiguous block to find the marker.
            in_list = False
            for back in range(i - 1, -1, -1):
                if not lines[back].strip():
                    break
                if LIST_ITEM_RE.match(lines[back]):
                    in_list = True
                    break
            if LIST_ITEM_RE.match(nxt) and in_list:
                return (f"defined at {where}, BETWEEN two list items — a block anchor does "
                        f"not attach there; make it inline: `- [[{anchor}]]item text...`")
            return f"defined at {where} but did not register; check the surrounding block"
    return "no `[[anchor]]` with this name exists in the checked documents"


def check(docs: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    sources = {d.name: d.read_text(encoding="utf-8", errors="replace").split("\n") for d in docs}

    with tempfile.TemporaryDirectory() as tmp:
        html = render_all(docs, Path(tmp))
        ids = {stem: set(ID_RE.findall(p.read_text(encoding="utf-8", errors="replace")))
               for stem, p in html.items()}

        for stem, path in sorted(html.items()):
            doc = stem + ".adoc"
            body = path.read_text(encoding="utf-8", errors="replace")
            for href, text in LINK_RE.findall(body):
                text = re.sub(r"<[^>]+>", "", text).strip()

                if ".adoc" in href and not href.startswith(("http://", "https://")):
                    findings.append(Finding(
                        doc, "BROKEN", f"`link:{href}` points at AsciiDoc source",
                        "a `link:` macro is not rewritten to .html — use `xref:file.adoc[text]`"))
                    continue

                target, _, anchor = href.partition("#")
                if href.startswith(("http://", "https://", "mailto:")):
                    continue

                if target == "":                                   # same-document
                    owner = stem
                elif target.endswith(".html"):                     # cross-document
                    owner = target[:-5]
                    if owner not in ids:
                        continue                                   # outside the checked set
                    if text == target:
                        findings.append(Finding(
                            doc, "POLISH", f"`xref:{owner}.adoc[]` renders as the filename "
                            f"“{target}”", "give the xref link text: `xref:file.adoc[Title]`"))
                else:
                    continue

                if anchor and anchor not in ids[owner]:
                    findings.append(Finding(
                        doc, "BROKEN", f"reference to `#{anchor}` does not resolve"
                        + ("" if owner == stem else f" in {owner}.adoc"),
                        diagnose(anchor, sources)))
                elif anchor and text == f"[{anchor}]":
                    findings.append(Finding(
                        doc, "POLISH", f"`<<{anchor}>>` renders as the literal “[{anchor}]”",
                        "the target block has no title — often an anchor placed BELOW its section "
                        "title instead of above it; move it above, or give the xref link text"))
    return findings


SELF_TEST_DOCS = {
    "good.adoc": (
        "= Good\n\n"
        "[[sec]]\n== Section\n\n"
        "<<sec>> resolves, and xref:other.adoc#there[cross doc] resolves.\n"
    ),
    "other.adoc": "= Other\n\n[[there]]\n== There\n\nBody.\n",
    "bad.adoc": (
        "= Bad\n\n"
        "[[one]]\n[[two]]\n.Titled block\nBody with <<two>> and <<one>>.\n\n"
        "== List\n\n"
        "- first item\nwrapped continuation line\n[[itemid]]\n- second item\n\n"
        "Refs: <<itemid>> and <<never-defined>> and link:other.adoc[src].\n"
    ),
}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for name, text in SELF_TEST_DOCS.items():
            (d / name).write_text(text, encoding="utf-8")
        findings = check(sorted(d.glob("*.adoc")))
        broken = {f.message for f in findings if f.severity == "BROKEN"}
        expected_broken = {
            "reference to `#one` does not resolve",       # consecutive anchors
            "reference to `#itemid` does not resolve",    # anchor above a list item
            "reference to `#never-defined` does not resolve",
            "`link:other.adoc` points at AsciiDoc source",
        }
        missed = expected_broken - broken
        # A finding is spurious if it is reported AGAINST a valid document.
        spurious = {f.message for f in findings
                    if f.severity == "BROKEN" and f.doc in ("good.adoc", "other.adoc")}
        if not missed and not spurious:
            print("self-test: PASS (detects consecutive anchors, an anchor between list "
                  "items, an undefined ref and a link:-to-source; no false positives)")
            return 0
        print("self-test: FAIL")
        if missed:
            print(f"  missed: {sorted(missed)}")
        if spurious:
            print(f"  false positives: {sorted(spurious)}")
        for f in findings:
            print(f.render())
        return 1


def collect(args: list[str]) -> list[Path]:
    docs: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            docs.extend(sorted(p.rglob("*.adoc")))
        elif p.is_file():
            docs.append(p)
        else:
            print(f"no such file or directory: {a}", file=sys.stderr)
            raise SystemExit(2)
    return docs


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: check-xrefs.py <file.adoc | directory> [...] | --self-test", file=sys.stderr)
        return 2
    if not shutil.which("asciidoctor"):
        print("asciidoctor is required (gem install asciidoctor)", file=sys.stderr)
        return 2
    if "--self-test" in args:
        return self_test()

    docs = collect(args)
    if not docs:
        print("no .adoc files found", file=sys.stderr)
        return 2
    if self_test() != 0:
        print("refusing to trust a checker that failed its own self-test", file=sys.stderr)
        return 1

    findings = check(docs)
    broken = [f for f in findings if f.severity == "BROKEN"]
    polish = [f for f in findings if f.severity != "BROKEN"]
    print(f"\nchecked {len(docs)} document(s)")
    for group, label in ((broken, "BROKEN"), (polish, "POLISH")):
        if group:
            print(f"\n{label} ({len(group)}):")
            for f in group:
                print(f.render())
    if not findings:
        print("  no cross-reference problems found")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
