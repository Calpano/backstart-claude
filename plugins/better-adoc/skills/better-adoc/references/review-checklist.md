# AsciiDoc review checklist

The ordered checklist for review mode. Work top to bottom; record each finding
with file:line, the checklist item, and a severity.

Severity rubric:

- **Broken** — renders wrongly or not at all; must fix.
- **Non-idiomatic** — renders, but violates the conventions; should fix.
- **Polish** — optional improvement; mention, fix only on request.

## 1. Markdown contamination (Broken)

Run `scripts/find-markdownisms.py <file>` first. Verify each hit before
recording it — hits inside listing/literal blocks (e.g. a `#` comment or a
URL in example code) are false positives, not findings:

- [ ] No `#` headings — use `=` levels.
- [ ] No ``` fenced code blocks — use `[source,lang]` + `----`.
- [ ] No `**bold**` / `__italic__` — use `*bold*` / `_italic_`.
- [ ] No `[text](url)` links — use `link:url[text]`.
- [ ] No manual `1.` `2.` list numbering — use `.` markers.
- [ ] No `---` horizontal rules, no `> ` blockquotes.

## 2. Document header (Non-idiomatic)

- [ ] Exactly one `= Title`, first non-comment line.
- [ ] `:toc:` present — every document gets a TOC.
- [ ] All attributes in the header block, not scattered through the body.
- [ ] Repeated literals (URLs, product names, versions, ≥3 occurrences)
      extracted into attributes (Polish).
- [ ] `:experimental:` present if `kbd:[]`/`btn:[]`/`menu:[]` are used
      (Broken if used without it).

## 3. Structure and anchors

- [ ] No skipped heading levels (`==` → `====`) (Broken — TOC nests wrongly).
- [ ] Every section has a `[[my-id]]` anchor on the line above the heading
      (Non-idiomatic). The `[#my-id]` form is a legal equivalent — normalize
      it to `[[my-id]]` (Polish, not Non-idiomatic).
- [ ] Blank line above each `[[id]]` anchor (Broken — the anchor may attach to
      the preceding block otherwise).
- [ ] Anchor is **above** its heading, never below it (Broken — below, it
      attaches to the following block and `<<id>>` renders as `[id]`).
- [ ] No two anchors on consecutive lines (Broken — only the last registers;
      make the other inline, `[[a]]Body text.`).
- [ ] No anchor **between** list items (Broken — it does not attach; use an
      inline anchor in the item text). Above the *first* item is fine.
- [ ] Nothing references a block title (`.My Table`) — not a valid target
      (Broken); give the block an explicit `[[id]]`.
- [ ] Anchor IDs are kebab-case and content-descriptive (Polish).
- [ ] No empty section stubs (Non-idiomatic).

## 4. Prose

- [ ] One sentence per line; no mid-sentence hard wraps (Non-idiomatic).
      Reflowing a whole existing document is one aggregate finding — ask
      before applying.
- [ ] No `+` line-break abuse at paragraph line ends (Non-idiomatic).
- [ ] No smart quotes pasted into code or attribute values (Broken).

## 5. Links and cross-references

- [ ] File-local section references use `<<id>>` against `[[id]]` anchors
      (Non-idiomatic).
- [ ] `<<id>>` targets all exist (Broken — renders as `[id]`).
- [ ] File links use `link:relative/path[label]` (Non-idiomatic).
- [ ] Web links use `link:https://…[label]` (Non-idiomatic).
- [ ] Nothing referenceable rendered as plain text or `code` — paths, URLs,
      and section names are clickable links (Non-idiomatic).
- [ ] No bare URLs where meaningful link text exists (Non-idiomatic).

## 6. Blocks

- [ ] Delimiters are exactly four characters and properly paired (Broken).
- [ ] Every listing block has `[source,lang]`; `text` if none applies
      (Non-idiomatic).
- [ ] JSON blocks use `json5`, not `json` (Non-idiomatic).
- [ ] Code explanation via callouts `<1>`, not prose-in-comments (Polish).
- [ ] Admonition levels match semantics — not everything is a WARNING
      (Polish).

## 7. Lists

- [ ] Every list has a `.Header` title line (Non-idiomatic).
- [ ] Term–definition pairs use `term:: definition`, not bold-lead-in bullets
      (Non-idiomatic).
- [ ] Definitions containing bullets are restructured as a headed list, not
      nested under the term (Non-idiomatic).
- [ ] Multi-block list content attached with `+` continuation (Broken if the
      block silently detaches from the list).
- [ ] Nesting ≤3 levels (Polish).

## 8. Images and tables

- [ ] Figures use block `image::` with alt text (Non-idiomatic; missing alt is
      accessibility-Broken).
- [ ] `:imagesdir:` set instead of repeated path prefixes (Polish).
- [ ] Tables declare `[cols=...]` and `options="header"` — no fake bold
      headers (Non-idiomatic).
- [ ] Two-narrow-column tables considered for conversion to a description
      list (Polish).

## 9. PlantUML diagrams

Check every `[plantuml]` block and referenced `.puml` file against the
checklist at the end of `references/plantuml.md`. Highlights:

- [ ] `hide circles` + `hide empty members` present (Non-idiomatic).
- [ ] Block has a `.Title` (Non-idiomatic).
- [ ] Styling uses `skinparam class { ...<<type>>... }` — a `<style>` block
      with aliased classes renders white boxes (Broken).
- [ ] Legend package present when types are color-styled (Non-idiomatic).

## 10. Render check (when asciidoctor is available)

```shell
asciidoctor --failure-level=WARN -o /dev/null <file>
```

- [ ] Zero warnings. Each warning (bad include path, unterminated block,
      malformed table) is a Broken finding at the reported line.

This does **not** cover cross-references. Asciidoctor performs no xref
validation whatsoever — an unresolved `<<bogus>>` renders as an ordinary link,
with no warning and exit code 0 — so a clean run here says nothing about them.

## 11. Cross-reference check

```shell
scripts/check-xrefs.py <file-or-directory>
```

Pass the whole directory when documents cross-link; `xref:other.adoc#id[]`
can only be verified when `other.adoc` is part of the same run.

- [ ] Zero `BROKEN` findings — dead `<<id>>`, dead `xref:doc.adoc#id[]`, or a
      `link:` macro pointing at `.adoc` source (Broken).
- [ ] Zero `POLISH` findings — an xref rendering as a bare filename or as the
      literal `[id]` (Polish).
