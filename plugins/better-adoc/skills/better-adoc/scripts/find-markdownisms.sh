#!/usr/bin/env bash
# find-markdownisms.sh — grep an .adoc file for Markdown syntax and common
# mechanical mistakes. Prints file:line:issue findings.
# Exit 0 = clean, 1 = findings, 2 = usage error.
set -euo pipefail

if [[ $# -ne 1 || ! -f "${1:-}" ]]; then
  echo "usage: $0 <file.adoc>" >&2
  exit 2
fi

file="$1"
found=0

# Prose-only view of the file: delimited blocks (----, ...., ====, ****, ++++,
# |=== tables) and inline code (`x`, ``x``, +++x+++) are blanked out, keeping
# line numbers intact. Without this, every URL in a JSON sample and every
# `https://ddot.it/CMD` code span is reported as a "bare URL" — hundreds of
# findings that are all wrong, which is worse than no check at all.
prose=$(awk '
  # Only VERBATIM containers are blanked: listing, literal and passthrough.
  # Example (====) and sidebar (****) blocks hold prose and must still be
  # checked — and treating them as toggles breaks nesting, which is how a JSON
  # sample inside a **** sidebar leaked through as a "bare URL".
  function isverbatim(l) { return (l ~ /^(-{4}|\.{4}|\+{4})$/) }
  {
    line = $0
    if (line ~ /^\/{4}$/) { incomment = !incomment; print ""; next }   # //// block
    if (incomment)        { print ""; next }
    if (isverbatim(line)) { inblock = !inblock; print ""; next }
    if (inblock)          { print ""; next }
    if (line ~ /^\/\//)   { print ""; next }                           # // line comment
    print line
  }' "$file" \
  | sed -E 's/`+[^`]*`+//g; s/\+\+\+[^+]*\+\+\+//g')

# check <pattern> <label>            — against prose only (content issues)
# check_raw <pattern> <label>        — against the file as written (structure)
check() {
  local pattern="$1" label="$2"
  local hits
  hits=$(printf '%s\n' "$prose" | grep -nE "$pattern" || true)
  if [[ -n "$hits" ]]; then
    found=1
    while IFS= read -r line; do
      echo "$file:${line%%:*}: $label :: ${line#*:}"
    done <<< "$hits"
  fi
}

check_raw() {
  local pattern="$1" label="$2"
  local hits
  hits=$(grep -nE "$pattern" "$file" || true)
  if [[ -n "$hits" ]]; then
    found=1
    while IFS= read -r line; do
      echo "$file:${line%%:*}: $label :: ${line#*:}"
    done <<< "$hits"
  fi
}

# --- Markdown contamination ---------------------------------------------------
check '^#{1,6} '                       'markdown heading (# ...) — use = levels'
check_raw '^```'                           'markdown fenced code block — use [source,lang] + ----'
check '\*\*[^*]+\*\*'                  'unconstrained bold (**x**) — valid AsciiDoc; prefer *x* unless it abuts word characters [style]'
check '(^|[^_])__[^_]+__([^_]|$)'      'markdown italic (__x__) — use _x_'
check '\[[^]]+\]\(https?://[^)]+\)'    'markdown link [text](url) — use link:url[text]'
check '^[[:space:]]*[0-9]+\. '         'manual list numbering (1.) — use . markers'
check '^---$|^—$'                      'markdown horizontal rule — use '"'''"''
check '^> '                            'markdown blockquote — use [quote] or ____'

# --- AsciiDoc mechanical issues ----------------------------------------------
check_raw '^-{5,}$'                        'listing delimiter longer than 4 chars — normalize to ----'
check_raw '^={5,}$'                        'block delimiter longer than 4 chars — normalize to ===='
check '^\[source\]$'                   '[source] without a language — add one (or text)'
check '^\[(source)?, ?json([],])'      '[source,json] — use json5 to avoid IDE warnings'
# bare URL in prose: skips attribute-definition lines (:url-x: https://...),
# and — via $prose — code blocks and inline code, where a URL is content.
check '^[^:].*https?://[^[ ]+([[:space:]]|$)|^https?://[^[ ]+([[:space:]]|$)' 'bare URL — wrap as link:url[text]'

# --- Header sanity ------------------------------------------------------------
if ! grep -qE '^:toc:' "$file"; then
  echo "$file:1: missing :toc: attribute — every document gets a TOC"
  found=1
fi
title_count=$(grep -cE '^= [^=]' "$file" || true)
if [[ "$title_count" -eq 0 ]]; then
  echo "$file:1: no level-0 title (= Title)"
  found=1
elif [[ "$title_count" -gt 1 ]]; then
  echo "$file:1: multiple level-0 titles ($title_count) — exactly one allowed"
  found=1
fi

if [[ "$found" -eq 0 ]]; then
  echo "clean: no markdown-isms or mechanical issues found in $file"
fi
exit "$found"
