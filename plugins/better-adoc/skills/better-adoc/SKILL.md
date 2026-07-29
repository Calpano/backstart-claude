---
name: better-adoc
description: This skill should be used when the user asks to "write AsciiDoc", "create an adoc file", "review this AsciiDoc", "clean up this .adoc", "improve my AsciiDoc", "lint an adoc file", asks about "AsciiDoc style" or "asciidoctor best practices", mentions "better-adoc", or when writing or substantially editing any .adoc file. It applies idiomatic Asciidoctor authoring conventions and runs a structured review of existing AsciiDoc documents.
---

# better-adoc

Write and review AsciiDoc that is idiomatic, diff-friendly, and renders cleanly
with Asciidoctor. The skill has two modes:

- **Authoring mode** — creating a new `.adoc` file or writing substantial new content into one.
- **Review mode** — auditing an existing `.adoc` file and reporting (or applying) improvements.

Pick the mode from the user's request. "Write / create / draft" → authoring.
"Review / lint / clean up / improve" → review. When editing an existing file,
apply the authoring rules to the new text without reformatting untouched
sections unless asked.

## Core authoring rules

These rules apply in both modes. The full rationale and extended examples are
in `references/style-guide.md`; consult it when a construct is not covered here.

### Structure

- Exactly one level-0 title (`= Title`) per document, in the header.
- **Always add a TOC** (`:toc:`).
- Never skip heading levels (`==` → `====` is wrong; go through `===`).
- **Give every section an identifier** via a `[[my-id]]` anchor on the line
  above the heading; the blank line above the anchor is required. Placement is
  not cosmetic — an anchor in the wrong place is silently dropped or attaches to
  the wrong element, and nothing warns:
  * Put it **above** the heading. Below the heading it attaches to the next
    block instead, so `<<my-id>>` renders as the literal `[my-id]`.
  * **One anchor per element.** With `[[a]]` and `[[b]]` on consecutive lines
    only the last registers; make the other an inline anchor
    (`[[a]]Body text starts here.`).
  * Above the **first** item of a list is fine (it labels the list); **between**
    items it does not attach — use an inline anchor in the item text.
  * A block title (`.My Table`) is **not** a cross-reference target. To link to
    a table or figure, give it an explicit `[[id]]`.

```asciidoc
= Document Title
Max Völkel <mv@maxvoelkel.de>
:toc:
:sectnums:
:icons: font
:source-highlighter: rouge

[[saas]]
== SaaS Software
Foo bla
```

- Define document-scoped facts as attributes and reference them with `{name}`
  instead of repeating literals (URLs, product names, versions):

```asciidoc
:url-repo: https://github.com/example/project

See the {url-repo}[project repository].
```

### Ventilated prose (one sentence per line)

Write **one sentence per line**. Do not hard-wrap mid-sentence and do not put
multiple sentences on one line. Asciidoctor joins consecutive lines into one
paragraph, so rendering is unaffected, while diffs, reviews, and edits become
sentence-granular. A blank line starts a new paragraph.

### Blocks

- Delimited block markers are **exactly four** characters: `----`, `====`, `****`, `____`.
- Source blocks always declare a language: `[source,python]` above `----`.
  For JSON, use `json5` (fewer IDE warnings).
- Use callouts (`<1>`) instead of inline comments to explain code lines.
- Admonitions: `NOTE:`, `TIP:`, `IMPORTANT:`, `WARNING:`, `CAUTION:` for one
  paragraph; the block form (`[NOTE]` + `====`) for multi-paragraph content.

### Lists, links, images, tables

- **Always give lists a header** (`.List Header` line above the list).
- Unordered lists use `*`; ordered lists use `.` (never manual `1.` numbering).
- Term–definition pairs use a description list: `my term:: my definition text`.
  If the definition text contains bullets, use a headed bullet list instead.
- Attach multi-block content to a list item with the `+` continuation line.
- **Everything referenceable is a clickable link** — never render a path, URL,
  or section name as plain text or `code`:
  * File-local section link: `<<saas>>` (against a `[[saas]]` anchor).
  * File link: `link:../path/path/file.ext[optional label]`.
  * Web link: `link:https://www.example.com[optional label]`.
  * Cross-file section: `xref:other.adoc#id[label]`.
- Never Markdown `[text](url)` syntax; never a bare URL when link text is possible.
- Images: block form `image::diagram.png[Alt text,600]` for figures (always
  provide alt text); inline form `image:icon.png[]` only inside a sentence.
- Tables: open with `[cols="1,2",options="header"]` and `|===`; keep one cell
  per line for non-trivial tables.

### PlantUML diagrams

Diagrams in `.adoc` files (and standalone `.puml` files) follow the
conventions in `references/plantuml.md`: titled `[plantuml]` blocks with `....`
delimiters, always `hide circles` + `hide empty members`, styling → classes →
relations ordering, lowerCamelCase names with `as "Title Cased Label"<<type>>`
stereotypes, type colors via `skinparam class { BackgroundColor<<type>> … }`
(never a `<style>` block — it renders aliased classes white), and a `Legend`
package for styled types. Read that file before writing or reviewing any
diagram.

### Not Markdown

AsciiDoc files must not contain Markdown habits. The most common offenders:

| Markdown-ism | AsciiDoc |
|---|---|
| `# Heading` | `= Heading` / `==` … |
| ` ``` ` fenced code | `[source,lang]` + `----` |
| `**bold**`, `__italic__` | `*bold*`, `_italic_` |
| `[text](url)` | `link:url[text]` |
| `1.` `2.` numbering | `.` per item |
| `---` horizontal rule | `'''` |
| `> quote` | `[quote]` block or `____` |

`scripts/find-markdownisms.py <file.adoc>` greps for these and other mechanical
issues; run it in review mode and optionally after authoring.

## Review mode workflow

To review an existing `.adoc` file, work through these steps in order:

1. **Mechanical scan** — run `scripts/find-markdownisms.py <file>` and note every hit.
2. **Read the document** — read the full file; check it against
   `references/review-checklist.md` top to bottom (structure, header, prose
   ventilation, blocks, links/xrefs, images, tables, semantics).
3. **Cross-reference check** — run
   `scripts/check-xrefs.py <file-or-directory>` and treat every `BROKEN`
   finding as a Broken-severity item, every `POLISH` finding as Polish.

   Do **not** rely on `asciidoctor --failure-level=WARN` for this. Asciidoctor
   does not validate cross-references at all: an unresolved `<<bogus>>` renders
   as an ordinary-looking link with no warning and exit code 0. Running it is
   still worthwhile for unterminated blocks and bad include paths, but a clean
   run says nothing about xrefs.

   Pass the whole directory, not one file, whenever the documents cross-link:
   `xref:other.adoc#id[]` can only be checked when `other.adoc` is included.
4. **Report** — list findings grouped by severity:
   * **Broken** — renders wrongly or not at all (bad block delimiters, dead xrefs, Markdown syntax).
   * **Non-idiomatic** — renders, but violates AsciiDoc conventions (bare URLs, skipped heading levels, unventilated prose).
   * **Polish** — optional improvements (attributes for repeated literals, admonition opportunities, table formatting).
5. **Apply** — fix the findings only when the user asked for fixes (e.g.
   "clean up", "fix"); for "review"/"check" requests, report and stop. When
   fixing, preserve the author's wording — change markup and structure, not
   voice or content.

Ventilating prose in an existing document is a large mechanical diff; in review
mode flag it as one finding and ask before reflowing an entire file.

## Authoring mode workflow

1. Establish the document type (README, article, reference page, book chapter) —
   it determines the header attributes and section depth.
2. Write the header first: title, author line if appropriate, needed attributes.
3. Draft content applying the core rules above, one sentence per line from the
   start.
4. Self-check against `references/review-checklist.md` before finishing, and
   run `scripts/find-markdownisms.py` and `scripts/check-xrefs.py` on the result.

## Additional resources

### Reference files

- **`references/style-guide.md`** — the full authoring style guide: rationale,
  extended examples, includes/partials, conditional content, UI macros,
  description lists, footnotes, and bibliography patterns.
- **`references/plantuml.md`** — PlantUML conventions for embedded and
  standalone diagrams: class syntax, stereotype styling (working skinparam
  form), Legend package, emoji flags, hyperlinks.
- **`references/review-checklist.md`** — the ordered checklist used in review
  mode, with a severity rubric for each item.

### Scripts

- **`scripts/find-markdownisms.py`** — Markdown contamination and mechanical
  issues. Takes files or directories. Findings are graded **BROKEN /
  NON-IDIOMATIC / STYLE** and map straight onto the review report's severities.
  Content rules run against a *prose view* (verbatim blocks, `//` comments and
  inline code blanked), so a URL in a JSON sample is not reported as a bare URL.
  Exit 1 on BROKEN or NON-IDIOMATIC, 0 when only STYLE remains (`--strict`
  makes STYLE fail too); `--self-test` proves it can still fail.
- **`scripts/check-xrefs.py`** — renders the documents and verifies every
  cross-reference against the ids that actually exist, because Asciidoctor
  itself reports none. Catches dead `<<id>>` and `xref:doc.adoc#id[]`, `link:`
  macros pointing at `.adoc` source, and empty-text xrefs that render as a bare
  filename — and diagnoses *why* an anchor failed to register. Takes files or
  directories; `--self-test` proves it can still fail. Exit 1 on BROKEN
  findings, 0 otherwise. Requires `asciidoctor` on PATH.
