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

## Isolating persona state

If the tool has mutable state (a database, a data directory, files on disk), each
persona needs its own copy so their writes do not contaminate another persona's
observations. Without this, a duplicate row or unexpected record one persona
"discovers" may simply be another persona's leftover — a false finding.

Always, before executing: **snapshot the tool's initial state**, and after the
run **restore it** so the user's real data is left untouched.

### Snapshot + restore

- Copy the tool's data location to a safe place first (`cp -r data data.orig`, or
  `git stash`/commit if the state is tracked). Restore it at the end.
- Prefer this over hand-editing or mutating the user's existing files in place —
  an in-place edit to pre-existing data may also be blocked as unsafe.

### Per-persona isolation for CLI tools

Choose the lightest option the tool supports:

1. **Configurable state location (best):** many CLIs take a data root via flag,
   env var, or config. Give each persona a fresh seeded copy and point the tool
   at it, e.g. per persona:
   `cp -r seed/ /tmp/uxrun-<runid>/<persona>/ && TOOL_ROOT=/tmp/uxrun-<runid>/<persona> htmldb ...`
   (or `htmldb config set rootDir …` scoped to that persona's shell).
2. **Copied working directory:** if state location is not configurable, run each
   persona in its own copy of the project (`cp -r`, or a `git worktree` per
   persona) so their filesystem writes are independent.
3. **Sequential + reset (fallback):** if neither is possible, run personas one at
   a time and reset state between them (restore from the snapshot, re-seed, or
   `git checkout -- <data>`). Note in each report that state was reset, or that it
   may have carried over if reset was not possible.

When personas run as parallel subagents (the recommended weaker-model setup),
isolation is mandatory — concurrent writes to one store interleave
unpredictably. Give each subagent its own root/copy in the prompt.

### Per-persona isolation for web apps

- Use a fresh browser context per persona: chrome-devtools `new_page` with a
  distinct `isolatedContext` name, or a fresh claude-in-chrome tab. This isolates
  cookies/session/storage, but **not** shared server state.
- The backend is the hard part: prefer a per-persona dev-server instance (each
  seeded from the same fixture), a reset/seed endpoint or script run before each
  persona, or per-persona accounts/tenants. If the app has one shared database
  and no reset, run personas sequentially and reset between them.
- Record which isolation was actually achieved; if backend state was shared, flag
  cross-persona findings as suspect.
