#!/usr/bin/env python3
"""find-markdownisms.py — Markdown contamination and mechanical issues in AsciiDoc.

    find-markdownisms.py <file.adoc | directory> [...] [--strict]
    find-markdownisms.py --self-test

Exit 0 = nothing worse than STYLE, 1 = BROKEN or NON-IDIOMATIC findings,
2 = usage error. With --strict, STYLE findings also exit 1.

DESIGN NOTES — every one of these is a bug this script actually had:

1. CHECK PROSE, NOT SOURCE. Content rules run against a view with listing /
   literal / passthrough blocks, `//` comments and inline code blanked out
   (line numbers preserved). Without it, every URL in a JSON sample and every
   `https://example.com` code span is reported. On one 8-document set that was
   189 "bare URL" findings, of which exactly 1 was real.

2. ONLY VERBATIM CONTAINERS TOGGLE BLOCK STATE. `====` and `****` hold prose
   and must still be checked; treating them as toggles also breaks nesting,
   which is how a JSON sample inside a sidebar leaked through.

3. `**x**` IS NOT REPORTED. It is unconstrained bold and renders as <strong>,
   which is what the author meant; `*x*` is pure taste, and the check produced
   234 findings that buried the 7 real ones. `__x__` IS reported, because it is
   not a taste question: AsciiDoc renders it ITALIC while Markdown means BOLD,
   so the habit silently changes meaning.

4. SEVERITY IS PART OF A FINDING. A flat list makes 229 cosmetic hits look like
   229 defects. Rules carry BROKEN / NON-IDIOMATIC / STYLE, and the exit code
   ignores STYLE so the script is usable in CI.

5. REPORT THE LINE AS WRITTEN. Matching happens on the stripped prose view;
   printing that view back is confusing, so findings quote the original line.

6. A LONGER DELIMITER IS NOT AN ERROR. `-----` renders identically to `----`
   (four is the minimum, not the maximum), so it is STYLE.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

BROKEN, NON_IDIOMATIC, STYLE = "BROKEN", "NON-IDIOMATIC", "STYLE"

VERBATIM_DELIM = re.compile(r"^(-{4,}|\.{4,}|\+{4,})\s*$")
COMMENT_BLOCK = re.compile(r"^/{4,}\s*$")
INLINE_CODE = re.compile(r"`+[^`]*`+|\+\+\+[^+]*\+\+\+")

# (severity, compiled pattern, message). Patterns marked raw=True see the file
# as written; the rest see the prose view.
RULES: list[tuple[str, re.Pattern[str], str, bool]] = [
    (BROKEN, re.compile(r"^#{1,6}\s+\S"), "Markdown heading (`# …`) — use `=` levels", False),
    (BROKEN, re.compile(r"^```"), "Markdown fenced code block — use `[source,lang]` + `----`", True),
    (BROKEN, re.compile(r"\[[^\]]+\]\((?:https?://|[./])[^)]+\)"),
     "Markdown link `[text](url)` — use `link:url[text]` or `xref:`", False),
    (BROKEN, re.compile(r"^>\s+\S"), "Markdown blockquote (`> …`) — use `[quote]` or `____`", False),

    (NON_IDIOMATIC, re.compile(r"^\[source\]\s*$"),
     "`[source]` without a language — add one (or `text`)", True),
    (NON_IDIOMATIC, re.compile(r"^\[(source)?,\s?json[\],]"),
     "`[source,json]` — use `json5` to avoid IDE warnings", True),
    (NON_IDIOMATIC, re.compile(r"^\s*\d+\.\s+\S"),
     "manual list numbering (`1.`) — use `.` markers", False),

    (STYLE, re.compile(r"^(-{5,}|={5,}|\*{5,}|_{5,})\s*$"),
     "delimiter longer than 4 characters — renders the same; normalise to 4", True),
]

# Bare URL. Two things make a URL NOT bare, and both are easy to get wrong:
#   * `link:https://…[…]` — the lookbehind rejects a preceding `:`;
#   * `https://…[label]` — AsciiDoc's macro form WITHOUT the `link:` prefix,
#     which is idiomatic and very common. A trailing `[` must therefore
#     disqualify the match, and it cannot be expressed as a lookahead: the
#     regex would simply backtrack to a shorter URL and match anyway. The
#     character after each match is checked in code instead.
BARE_URL = re.compile(r"(?<![\w:\[])https?://[^\s\[\]]+")


def bare_urls(line: str) -> bool:
    return any(line[m.end():m.end() + 1] != "[" for m in BARE_URL.finditer(line))
ATTR_DEF = re.compile(r"^:[\w-]+:")

# `**x**` is NOT checked at all. It is unconstrained bold, it renders as
# <strong> — exactly what a Markdown author meant — and the constrained `*x*`
# offers no benefit beyond taste. Nagging about it produced 234 findings on one
# document set and buried everything that mattered.
#
# `__x__` IS checked, and not as a style preference: AsciiDoc renders it as
# <em> (italic), whereas in Markdown it means BOLD. A Markdown habit here
# silently changes the meaning, which is the one case in this family that is a
# real defect rather than a spelling choice.
MARKDOWN_BOLD_UNDERSCORE = re.compile(r"(?<!\w)__(?!\s)([^_\n]+?)(?<!\s)__(?!\w)")


def prose_view(lines: list[str]) -> list[str]:
    """Same length as `lines`, with verbatim blocks/comments/inline code blanked."""
    out: list[str] = []
    in_block = in_comment = False
    for line in lines:
        if COMMENT_BLOCK.match(line):
            in_comment = not in_comment
            out.append("")
            continue
        if in_comment:
            out.append("")
            continue
        if VERBATIM_DELIM.match(line):
            in_block = not in_block
            out.append("")
            continue
        if in_block or line.lstrip().startswith("//"):
            out.append("")
            continue
        out.append(INLINE_CODE.sub("", line))
    return out


def check_file(path: Path) -> list[tuple[str, int, str, str, str]]:
    """-> [(severity, lineno, message, original_line, file)]"""
    raw = path.read_text(encoding="utf-8", errors="replace").split("\n")
    prose = prose_view(raw)
    found: list[tuple[str, int, str, str, str]] = []

    def add(sev: str, i: int, msg: str) -> None:
        found.append((sev, i + 1, msg, raw[i].strip(), path.name))

    for sev, pat, msg, use_raw in RULES:
        for i, line in enumerate(raw if use_raw else prose):
            if pat.search(line):
                add(sev, i, msg)

    for i, line in enumerate(prose):
        if line and not ATTR_DEF.match(line) and bare_urls(line):
            add(NON_IDIOMATIC, i, "bare URL — wrap as `link:url[text]`")
        if MARKDOWN_BOLD_UNDERSCORE.search(line):
            add(NON_IDIOMATIC, i, "`__x__` renders as *italic* in AsciiDoc, but means **bold** "
                                  "in Markdown — use `*x*` for bold, `_x_` for italic")

    text = "\n".join(raw)
    if not re.search(r"^:toc:", text, re.M):
        found.append((NON_IDIOMATIC, 1, "missing `:toc:` attribute — every document gets a TOC",
                      raw[0].strip() if raw else "", path.name))
    titles = len(re.findall(r"^= [^=]", text, re.M))
    if titles == 0:
        found.append((BROKEN, 1, "no level-0 title (`= Title`)", "", path.name))
    elif titles > 1:
        found.append((BROKEN, 1, f"{titles} level-0 titles — exactly one allowed", "", path.name))

    return sorted(found, key=lambda f: (f[1], f[0]))


SELF_TEST = {
    "clean.adoc": (
        "= Clean\n:toc:\n\n"
        "Prose with a link:https://example.com[proper link], a https://example.org[bare-form macro]\n"
        "and `https://in-code.example` inline.\n\n"
        "[source,text]\n----\nhttps://inside-a-block.example/x\n**not markdown here**\n----\n\n"
        "// https://in-a-comment.example\n\n"
        "Both **re**structure and **plain bold** stay unflagged.\n"
    ),
    "dirty.adoc": (
        "= Dirty\n:toc:\n\n"
        "# markdown heading\n\n"
        "A [markdown link](https://example.com) here.\n\n"
        "> a blockquote\n\n"
        "Visit https://bare.example/page for more.\n\n"
        "This __looks bold__ but renders italic.\n\n"
        "[source]\n----\nx\n----\n"
    ),
}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for name, text in SELF_TEST.items():
            (d / name).write_text(text, encoding="utf-8")

        clean = check_file(d / "clean.adoc")
        dirty = check_file(d / "dirty.adoc")
        problems: list[str] = []

        if clean:
            problems.append("clean.adoc should yield no findings, got: "
                            + "; ".join(f"{s} L{n} {m}" for s, n, m, _, _ in clean))

        want = {
            (BROKEN, "Markdown heading"), (BROKEN, "Markdown link"), (BROKEN, "Markdown blockquote"),
            (NON_IDIOMATIC, "bare URL"), (NON_IDIOMATIC, "`[source]` without a language"),
            (NON_IDIOMATIC, "`__x__` renders as"),
        }
        for sev, frag in want:
            if not any(s == sev and frag in m for s, _, m, _, _ in dirty):
                problems.append(f"dirty.adoc: missed {sev} {frag!r}")

        if problems:
            print("self-test: FAIL")
            for p in problems:
                print("  " + p)
            return 1
        print("self-test: PASS (flags 6 planted issues; no false positives on code blocks, "
              "inline code, comments, or any form of **bold**)")
        return 0


def collect(args: list[str]) -> list[Path]:
    out: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.adoc")))
        elif p.is_file():
            out.append(p)
        else:
            print(f"no such file or directory: {a}", file=sys.stderr)
            raise SystemExit(2)
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--strict"]
    strict = "--strict" in sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    if not args:
        print("usage: find-markdownisms.py <file.adoc | directory> [...] [--strict] | --self-test",
              file=sys.stderr)
        return 2
    if self_test() != 0:
        print("refusing to trust a checker that failed its own self-test", file=sys.stderr)
        return 1

    files = collect(args)
    findings = [f for p in files for f in check_file(p)]
    counts = {BROKEN: 0, NON_IDIOMATIC: 0, STYLE: 0}
    print(f"\nchecked {len(files)} file(s)")
    for sev in (BROKEN, NON_IDIOMATIC, STYLE):
        group = [f for f in findings if f[0] == sev]
        counts[sev] = len(group)
        if not group:
            continue
        print(f"\n{sev} ({len(group)}):")
        for _, line, msg, text, name in group:
            print(f"  {name}:{line}: {msg}")
            if text:
                print(f"      | {text[:100]}")
    if not findings:
        print("  clean — no Markdown-isms or mechanical issues")
    else:
        print(f"\nsummary: {counts[BROKEN]} broken, {counts[NON_IDIOMATIC]} non-idiomatic, "
              f"{counts[STYLE]} style")
    return 1 if counts[BROKEN] or counts[NON_IDIOMATIC] or (strict and counts[STYLE]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
