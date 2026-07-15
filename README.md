# better-ux

A Claude Code plugin that runs structured **usability tests** on web apps and CLI
tools. It plays a panel of fictional users who each pursue a real goal, narrate
their reasoning aloud (the *think-aloud* technique), and log every assumption,
action, and surprise. Each run ends with a ranked, evidence-backed list of UX
improvements.

## What it does

1. **Intake** — asks how to run the tool (URL, dev-server command, or CLI path)
   and where its intended behavior is described (homepage, `--help`, README).
2. **Scenarios** — brainstorms persona-driven scenarios into `scenarios/`
   (`scenario-alice.adoc`, `scenario-bob.adoc`, …). Default 5, up to 20.
3. **Execution** — walks each scenario with the think-aloud loop, writing one
   report per scenario: `reports/YYYY-MM-DD-<persona>-<runid>.adoc`.
4. **Distillation** — reads all reports in a run and produces a ranked
   `reports/improvements-<runid>.adoc`.

All artifacts are AsciiDoc (`.adoc`).

## Install

Local development:

```bash
cc --plugin-dir /path/to/better-ux
```

Or add the repo to a plugin marketplace and install it from there.

## Use

In a session inside the project you want to test:

> UX test my web app at http://localhost:3000 — generate 5 scenarios

The `better-ux` skill triggers on phrases like "UX test", "usability test",
"run a UX review", "think-aloud test", or "evaluate the usability of".

Web execution uses the [claude-in-chrome](https://www.anthropic.com) browser
automation MCP; CLI execution uses the shell.

## Layout

```
better-ux/
├── .claude-plugin/plugin.json
└── skills/better-ux/
    ├── SKILL.md
    ├── assets/          # AsciiDoc templates (scenario, report, improvements)
    └── references/      # personas, think-aloud method, driving recipes
```

## License

MIT
