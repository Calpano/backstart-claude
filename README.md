# backstart.io — Claude Code plugins

A single marketplace hosting the plugins below. Each lives in `plugins/` and is
released independently via its own `plugin.json` version.

| Plugin | What it does |
|---|---|
| [`better-adoc`](plugins/better-adoc) | Write and review idiomatic AsciiDoc: authoring style rules and a lint-style review workflow. |
| [`better-ux`](plugins/better-ux) | Persona-driven, think-aloud usability testing for web apps and CLI tools. |

## Install

```shell
claude plugin marketplace add /path/to/backstart-claude
claude plugin install better-adoc@backstart.io
claude plugin install better-ux@backstart.io
```

Plugins install from a *copy* taken at install time, so after editing a plugin
run `claude plugin update <name>@backstart.io` to pick the changes up, then
restart the session.

## Layout

```
.claude-plugin/marketplace.json   the backstart.io marketplace (lists both plugins)
plugins/<name>/                   one plugin each: .claude-plugin/plugin.json,
                                  commands/, skills/
```

A plugin's `source` must be a path *inside* this repo (or a GitHub repo) —
sibling and absolute paths are rejected by the manifest schema, which is why
the plugins live here rather than beside it.
