---
description: Write or review AsciiDoc using idiomatic authoring conventions
argument-hint: '[file.adoc or topic] [review | fix]'
---

Run the **better-adoc** workflow.

Follow the skill instructions at `${CLAUDE_PLUGIN_ROOT}/skills/better-adoc/SKILL.md`
exactly. Pick the mode from the arguments: an existing `.adoc` file with
"review" → review mode (report only); with "fix" → review mode with fixes
applied; a topic or new filename → authoring mode. Consult the skill's
`references/` and run its `scripts/find-markdownisms.sh` as directed there.

Target and options the user provided: $ARGUMENTS

If no target was provided, ask whether to write a new document or review an
existing one, and for the file path or topic.
