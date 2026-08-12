# backstart.io — Claude Code plugins

A single marketplace hosting the plugins below. Each lives in `plugins/` and is
released independently via its own `plugin.json` version.

| Plugin | What it does |
|---|---|
| [`better-adoc`](plugins/better-adoc) | Write and review idiomatic AsciiDoc: authoring style rules and a lint-style review workflow. |
| [`better-ux`](plugins/better-ux) | Persona-driven, think-aloud usability testing for web apps and CLI tools. |

## Install

```shell
claude plugin marketplace add Calpano/backstart-claude
claude plugin install better-adoc@backstart.io
claude plugin install better-ux@backstart.io
```

Restart the session afterwards. To move to a newer release later, run
`claude plugin update <name>@backstart.io`.

## Development

Plugins install from a *copy* taken at install time, so working on them here
means adding the local checkout instead of the GitHub one:

```shell
claude plugin marketplace add .
```

After each edit run `claude plugin update <name>@backstart.io` to pick the
changes up, then restart the session.

## Releasing

Plugins are pinned to tags, so a release is two commits and the order matters:

1. Bump `plugins/<name>/.claude-plugin/plugin.json`, commit, and tag:
   `claude plugin tag plugins/<name>` — it creates `<name>--v<version>` and
   checks that plugin.json and the marketplace entry agree.
2. Point the marketplace entry at that tag: set `ref` to the tag name and `sha`
   to **the commit the tag points at**. Commit and push both.

The `sha` must be the *commit*, not the tag object. Annotated tags are objects
with their own hash, and `git ls-remote` shows that hash — pinning it fetches
nothing. Peel it:

```shell
git rev-list -n 1 <name>--v<version>
```

Because the entry names a tag that must already exist, the manifest commit
necessarily comes *after* the tag. Consumers then get an exact, immutable
version: moving the tag later does not change what they install, since `sha`
wins.

## Layout

```
.claude-plugin/marketplace.json   the backstart.io marketplace (lists both plugins)
plugins/<name>/                   one plugin each: .claude-plugin/plugin.json,
                                  commands/, skills/
```

A plugin's `source` must be a path *inside* this repo (or a GitHub repo) —
sibling and absolute paths are rejected by the manifest schema, which is why
the plugins live here rather than beside it.
