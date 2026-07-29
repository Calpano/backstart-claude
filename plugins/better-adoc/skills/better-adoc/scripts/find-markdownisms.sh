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

check() {
  local pattern="$1" label="$2"
  # grep -n over the file; prefix each hit with the issue label
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
check '^```'                           'markdown fenced code block — use [source,lang] + ----'
check '\*\*[^*]+\*\*'                  'markdown bold (**x**) — use *x*'
check '(^|[^_])__[^_]+__([^_]|$)'      'markdown italic (__x__) — use _x_'
check '\[[^]]+\]\(https?://[^)]+\)'    'markdown link [text](url) — use link:url[text]'
check '^[[:space:]]*[0-9]+\. '         'manual list numbering (1.) — use . markers'
check '^---$|^—$'                      'markdown horizontal rule — use '"'''"''
check '^> '                            'markdown blockquote — use [quote] or ____'

# --- AsciiDoc mechanical issues ----------------------------------------------
check '^-{5,}$'                        'listing delimiter longer than 4 chars — normalize to ----'
check '^={5,}$'                        'block delimiter longer than 4 chars — normalize to ===='
check '^\[source\]$'                   '[source] without a language — add one (or text)'
check '^\[(source)?, ?json([],])'      '[source,json] — use json5 to avoid IDE warnings'
# bare URL: skip attribute-definition lines (:url-x: https://...) — those are the
# recommended single-source-of-truth pattern. May still hit URLs inside listing
# blocks; treat such hits as advisory, not findings.
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
