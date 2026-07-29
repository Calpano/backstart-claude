# better-adoc

A Claude Code plugin for writing and reviewing **idiomatic AsciiDoc**. It
encodes a concrete house style — ventilated prose, explicit `[[id]]` anchors,
`link:` macros everywhere, headed lists, `json5` code blocks, and PlantUML
diagram conventions — and applies it in two modes:

- **Authoring** — new `.adoc` content follows the style from the first line.
- **Review** — existing files are audited against an ordered checklist and
  findings are reported as Broken / Non-idiomatic / Polish (fixes applied on
  request).

## What it enforces (highlights)

- One sentence per line (diff-friendly "ventilated prose").
- Always a `:toc:`; every section gets a stable `[[kebab-case-id]]` anchor.
- Clickable links everywhere: `<<id>>` for local sections,
  `link:path[label]` for files, `link:https://…[label]` for the web —
  never bare URLs or Markdown syntax.
- Every list has a `.Header`; term–definition pairs use `term:: definition`.
- `[source,lang]` on every listing; `json5` instead of `json`.
- PlantUML: `hide circles` + `hide empty members`, typed classes with
  stereotype colors via the working `skinparam class` form (not `<style>`
  blocks, which render aliased classes white in PlantUML 1.2026.x), and a
  Legend package.

Two deterministic checkers back the review mode
(`skills/better-adoc/scripts/`):

- `find-markdownisms.sh` — greps for Markdown contamination and mechanical
  mistakes.
- `check-xrefs.py` — renders the `.adoc` sources and verifies every
  cross-reference, since Asciidoctor itself reports none; diagnoses why an
  anchor failed to register.

## Install

Local development:

```bash
cc --plugin-dir /path/to/better-adoc
```

Or add the repo to a plugin marketplace and install it from there.

## Use

The `better-adoc` skill triggers on phrases like "write AsciiDoc", "review
this .adoc", "clean up this AsciiDoc", "asciidoc style", or whenever writing
or substantially editing a `.adoc` file. There is also an explicit command:

> /better-adoc docs/architecture.adoc review

## Layout

```
better-adoc/
├── .claude-plugin/plugin.json
├── commands/better-adoc.md
└── skills/better-adoc/
    ├── SKILL.md
    ├── references/   # style-guide, plantuml conventions, review checklist
    └── scripts/      # find-markdownisms.sh, check-xrefs.py
```

## License

MIT
