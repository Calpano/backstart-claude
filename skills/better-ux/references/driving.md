# Driving the tool under test

Concrete recipes for exercising the tool during Phase 3 execution. Choose the
section matching the tool type established in intake.

## Web apps — browser automation

Web scenarios need a browser-automation MCP. Two work well; **prefer
chrome-devtools-mcp** — it is a plain `npx` install with no browser extension,
so it is reliable in fresh and headless environments.

### Ensure a driver is installed (do this in Phase 1 for web tools)

Before executing web scenarios, confirm a driver is available. If neither the
`mcp__chrome-devtools__*` nor the `mcp__claude-in-chrome__*` tools are present,
offer to install **chrome-devtools-mcp** (https://github.com/ChromeDevTools/chrome-devtools-mcp)
and give the user the one-line command for their client:

```bash
# Claude Code
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

For other clients, add this to the MCP config and restart:

```json
{ "mcpServers": { "chrome-devtools": { "command": "npx", "args": ["chrome-devtools-mcp@latest"] } } }
```

Requirements: Node ≥ 20 and a local Chrome. After install, the client must be
restarted for the tools to load. If the user declines or install fails, fall
back to claude-in-chrome (below); if that is also unavailable, verify web claims
structurally instead (inspect the served HTML/DOM) and record that live
rendering was not performed.

### chrome-devtools-mcp (preferred)

If its tools are deferred, load them in one ToolSearch call:

```
select:mcp__chrome-devtools__new_page,mcp__chrome-devtools__navigate_page,mcp__chrome-devtools__take_snapshot,mcp__chrome-devtools__take_screenshot,mcp__chrome-devtools__click
```

Map think-aloud moves onto its tools (full loop in `think-aloud.md`):
- **Start** → `new_page` with the app URL (start a dev server first if intake specified one).
- **Scan** → `take_snapshot` (accessibility tree with element `uid`s) — read only what a user perceives.
- **Act** → `click`/`fill`/`type_text` targeting an element `uid` from the latest snapshot. One action per step.
- **Observe** → a fresh `take_snapshot`; `take_screenshot` (saved to a workspace-root path) for every SURPRISING result as evidence.

### claude-in-chrome (fallback / when already present)

Drives a real Chrome tab via an extension. If deferred, load in one call:

```
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find
```

Call `tabs_context_mcp` first; create a fresh tab with `tabs_create_mcp` (do not
reuse an existing tab unless asked); `navigate` to the URL. Then **Scan** with
`read_page`, **Act** with `computer`/`find`, **Observe** with `read_page`/screenshot.

### Cautions (both drivers)

- Never trigger native `alert`/`confirm`/`prompt` dialogs — they can freeze the
  session. Avoid controls that raise them; warn the user if a step requires one.
- If a tool call fails 2–3 times or the page will not load, stop and ask the
  user rather than looping.
- Record concrete element labels/uids acted on so a reader can reproduce the step.

## CLI tools — Bash

Exercise the CLI exactly as the persona would, from their described context.

Startup:
- Run any install/build step from intake first (e.g. `npm install`, `make`).
- Confirm the invocation path works (`which <tool>` or `./tool --version`).

Run the think-aloud loop (see `think-aloud.md`) with these CLI specifics:
- **Scan** the last output the persona saw (help text, prompt, previous result).
- **Act** by running one command as typed by the persona. Deliberately try what
  a real user would guess, including "wrong" but reasonable guesses.
- **Observe** by capturing stdout, stderr, and the exit code.

CLI-specific UX findings to watch for:
- No output on success (silence that leaves the user unsure it worked).
- Cryptic errors, stack traces, or non-zero exits with no guidance.
- Missing or unhelpful `--help`; flags that do not match the help text.
- Bad or dangerous defaults; destructive actions without confirmation.
- Inconsistent naming (`--dry-run` here, `-n` there) across subcommands.
- Poor discoverability: no way to list subcommands, no examples.

Treat a "wrong guess that a reasonable user would make" as a first-class test —
if the tool punishes it harshly instead of guiding, that is a finding.

## Both

For tools with a web and a CLI surface, run scenarios against whichever surface
the persona's context implies, and note in the report which surface was tested.
