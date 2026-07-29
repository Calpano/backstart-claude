# AsciiDoc authoring style guide

Extended rules and rationale behind the core rules in SKILL.md. Grounded in
Asciidoctor's recommended practices and the conventions used by large AsciiDoc
projects (Asciidoctor docs, Spring, Quarkus, the Antora ecosystem).

## Document header

The header is everything from the `=` title to the first blank line. Rules:

- The title is the only level-0 heading. Section titles start at `==`.
- The optional author line follows the title immediately: `Firstname Lastname <email>`.
- A revision line may follow the author line: `v1.2, 2026-07-29: Summary`.
- All document attributes belong in the header, one per line, before the first
  blank line. Attributes set later in the body apply only from that point and
  surprise future editors.

**Always add a TOC** (`:toc:` in the header). Common attribute sets by
document type:

```asciidoc
= Project README
:toc: preamble
:icons: font
:source-highlighter: rouge

= Technical article
:toc:
:sectnums:
:icons: font
:source-highlighter: rouge
:xrefstyle: short

= Reference / manual page
:toc: left
:sectnums:
:sectlinks:
:sectanchors:
```

Notes:

- `:icons: font` renders admonition icons instead of the text label.
- `:source-highlighter:` — `rouge` is the current default choice for
  Asciidoctor; `highlight.js` for pure-HTML pipelines.
- `:experimental:` is required before using `kbd:[]`, `btn:[]`, `menu:[]`.
- `:xrefstyle: short` makes `xref` text render as "Section Title" rather than
  "Section 1.2, 'Section Title'".

## Attributes as single source of truth

Define once, reference everywhere:

```asciidoc
:product: WidgetServer
:version: 3.2
:url-docs: https://docs.example.org

{product} {version} is documented at {url-docs}[the docs site].
```

Use attributes for: product/project names, versions, base URLs, dates, and any
literal that appears three or more times. Name URL attributes with a `url-`
prefix. Do not use attributes for one-off values — indirection without reuse
hurts readability.

Attribute references are substituted inside most text but **not** inside
literal/listing blocks unless the block enables it with `[subs="attributes"]`
(or `subs="attributes+"` to add to the defaults).

## Ventilated prose in depth

One sentence per line ("ventilated" or "semantic line breaks"):

- Renders identically: consecutive non-blank lines form one paragraph.
- Diffs show exactly which sentence changed; review comments can target one
  sentence.
- Reordering sentences is a line move, not a re-wrap of a whole paragraph.
- Very long sentences become visible as very long lines — a useful writing
  smell.

A clause break may also get its own line when the sentence is long (break after
commas, before conjunctions), but never break mid-clause just to satisfy a line
length. Do not enforce a column limit on `.adoc` prose.

## Sections and anchors

- Never skip levels. Asciidoctor logs a warning and the TOC nests wrongly.
- **Give every section an identifier** using the `[[my-id]]` block-anchor form
  on the line directly above the heading. A **blank line above the anchor is
  required**:

```asciidoc

[[saas]]
== SaaS Software
Foo bla
```

- Auto-generated IDs change when the title is edited; explicit `[[id]]` anchors
  are stable.
- Anchor naming: kebab-case, content-descriptive (`[[install-linux]]`, not
  `[[sec3]]`).
- `:sectanchors:` + `:sectlinks:` make headings self-linkable in HTML output —
  recommended for reference documentation.

## Cross-references and links

**Everything referenceable is a clickable link** — sections, files, and URLs.
Never render a path, URL, or section name as plain text or `code` when a link
is possible.

```asciidoc
See <<saas>> for details.                          // file-local section link
See <<saas,the SaaS chapter>> for details.         // …with custom text
See xref:install.adoc#linux[Linux install].        // section in another file
See link:../path/path/file.ext[optional label].    // file link
See link:https://www.example.com[optional label].  // web link
```

Rules:

- File-local section links use `<<id>>` against a `[[id]]` anchor.
- File links use the `link:` macro with a relative path.
- Web links also use the `link:` macro (`link:https://…[label]`).
- Never paste a bare URL when meaningful link text exists. A bare URL is
  acceptable only when the URL itself is the information (e.g. in a reference
  list).
- Mail links: `mailto:mv@example.org[Max]`.

## Blocks

### Delimiters

Exactly four characters, on their own line, matching pairs:

| Delimiter | Block |
|---|---|
| `----` | listing / source |
| `....` | literal |
| `====` | example / admonition body |
| `****` | sidebar |
| `____` | quote / verse |
| `\|===` | table |
| `--` | open block (2 chars — the exception) |

Longer delimiter runs (`-----------`) are a legacy habit; normalize to four.

### Source blocks

```asciidoc
[source,java]
----
public class Widget { }   // <1>
----
<1> Callout explanation goes here.
```

- Always specify the language (use `text` when none applies).
- For JSON blocks, use the `json5` language type instead of `json` — it
  produces fewer IDE warnings (trailing commas, comments).
- Callouts (`<1>` … in code, matching `<1>` list after the block) replace
  explanatory inline comments.
- Add a block title with `.Title` on the line above `[source,...]` when the
  listing is referenced from prose.
- Use `[,java]` shorthand only in projects that already use it; the explicit
  `[source,java]` is clearer.

### Admonitions

```asciidoc
NOTE: Single-paragraph form.

[WARNING]
====
Multi-paragraph form.

Second paragraph.
====
```

Severity semantics: `NOTE` (aside), `TIP` (better way), `IMPORTANT` (must
read), `WARNING` (risk of damage/data loss), `CAUTION` (physical/irreversible
risk). Do not escalate for emphasis — a document where everything is a WARNING
has no warnings.

## Lists

**Always give lists a header** (a `.Title` line directly above the list):

```asciidoc
.List Header
* Item 1
* Item 2
** Nested item

.Steps
. Ordered item
. Next item — numbering is automatic
+
Continuation paragraph attached to this item.
+
[source,shell]
----
echo "blocks attach with + too"
----
```

For term–definition pairs, use a description list:

```asciidoc
my term:: my definition text
```

- If a definition text would contain bullets, do not nest them under the
  term — use a headed bullet list instead.
- `*` / `.` markers, depth by repetition; never manual numbers.
- The `+` continuation line attaches paragraphs and blocks to a list item.
- Checklists: `* [x]` / `* [ ]`.
- Use description lists (`term::`) for option/parameter documentation — they
  are semantic and render better than abused bullet lists.

## Images and media

```asciidoc
:imagesdir: images

.Figure caption
image::architecture.png[Architecture overview,800]

Click the image:save-icon.png[Save icon] icon.
```

- Block macro `image::` (two colons) for figures; inline `image:` (one colon)
  only within a sentence.
- Alt text is mandatory; width in pixels as second positional attribute when
  the source is large.
- Set `:imagesdir:` in the header instead of repeating path prefixes.

## Tables

```asciidoc
.Supported platforms
[cols="1,2,1",options="header"]
|===
|Platform |Notes |Status

|Linux
|Primary target
|Supported

|macOS
|CI-tested
|Supported
|===
```

- `cols` declares relative widths (and per-column styles: `a` for AsciiDoc
  content in cells, `<`/`^`/`>` alignment).
- `options="header"` — do not fake a header with bold text.
- One cell per line, blank line between rows, for any table wider than ~2 short
  columns; single-line rows are fine for compact matrices.
- Reach for a description list or plain prose before a table with only two
  narrow columns.

## Includes and modular documents

```asciidoc
include::partials/prerequisites.adoc[]
include::chapters/install.adoc[leveloffset=+1]
include::../src/main/java/Widget.java[tag=core,indent=0]
```

- Included chapter files start at `= Title` and are mounted with
  `leveloffset=+1` — this keeps each file independently renderable.
- Use `tag=`/`tags=` regions to include code snippets from real source files
  instead of copy-pasting code into the document.
- Guard partials that must not render standalone with a `_` filename prefix
  (Antora convention: `partials/` directory).

## PlantUML diagrams

Embed diagrams as titled `[plantuml]` blocks with `....` delimiters. All
diagram conventions — class syntax, stereotype styling, Legend package, emoji
flags — are in `plantuml.md` (same directory). Read it before writing or
reviewing any diagram.

## Conditional content

```asciidoc
ifdef::backend-pdf[]
This appears only in the PDF.
endif::[]

ifndef::env-github[]
GitHub's renderer does not support this feature.
endif::[]
```

Useful built-in attributes: `env-github` (set by GitHub's renderer),
`backend-html5`, `backend-pdf`. GitHub renders a *subset* of AsciiDoc — no
`include::`, limited attributes — so READMEs destined for GitHub should avoid
includes or provide `ifdef::env-github[]` fallbacks.

## UI macros, keyboard, and inline semantics

Requires `:experimental:` in the header:

```asciidoc
Press kbd:[Ctrl+Shift+P].
Click btn:[Save].
Choose menu:File[Export > PDF].
```

Other inline markup:

- `` `monospace` `` for code, filenames, commands, literal values.
- `*bold*` for UI names without the macros, and sparingly for emphasis.
- `_italic_` for introduced terms and titles of works.
- `+literal+` passthrough when the text contains characters AsciiDoc would
  otherwise interpret.
- Apostrophes/quotes: write plain `'` and `"`; use `` `'` `` typographic forms
  only in projects that already do.

## Footnotes and bibliography

```asciidoc
A claim.footnote:[Source or aside text.]
A repeated note.footnote:disclaimer[Shared footnote text.]
```

For articles with real citations, prefer a `[bibliography]` section with
`[[[ref-id]]]` entries and `<<ref-id>>` citations over ad-hoc footnotes.

## Things to avoid

- Markdown syntax of any kind (see the table in SKILL.md).
- `+` at line end for line breaks in prose — restructure instead; hard breaks
  belong only in verses and addresses (`[%hardbreaks]`).
- Deeply nested lists (>3 levels) — restructure into sections.
- Roles/inline styles (`[.red]#text#`) for meaning — color is not semantics.
- Empty section stubs; every section has at least one paragraph.
- Smart-quote characters pasted from word processors inside code or attribute
  values.
