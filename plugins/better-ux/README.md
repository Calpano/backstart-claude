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

```shell
claude plugin marketplace add Calpano/backstart-claude
claude plugin install better-ux@backstart.io
```

Restart the session afterwards. For local development, point `--plugin-dir` at
a checkout of this directory instead: `claude --plugin-dir /path/to/better-ux`.

## Use

In a session inside the project you want to test:

> UX test my web app at http://localhost:3000 — generate 5 scenarios

The `better-ux` skill triggers on phrases like "UX test", "usability test",
"run a UX review", "think-aloud test", or "evaluate the usability of". To
invoke it explicitly:

> /better-ux:better-ux http://localhost:3000 5 scenarios

Web execution uses a browser-automation MCP — preferring
[chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
(`claude mcp add chrome-devtools npx chrome-devtools-mcp@latest`), falling back
to claude-in-chrome; the skill offers to install one if none is present. CLI
execution uses the shell.

**Tip:** run the walkthrough phase with a deliberately weaker model (Haiku or
Sonnet). A frontier model powers through confusing UI that would stop a real
user and hides the friction; a weaker model stumbles where real users do,
surfacing more genuine UX problems.

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
