# Driving the tool under test

Concrete recipes for exercising the tool during Phase 3 execution. Choose the
section matching the tool type established in intake.

## Web apps — claude-in-chrome MCP

The claude-in-chrome MCP drives a real Chrome tab. If its tools are deferred,
load them first in one ToolSearch call:

```
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find
```

Startup sequence:

1. If intake specified a dev server, start it first with Bash in the background
   (e.g. `npm run dev`), and wait until it serves before navigating.
2. Call `tabs_context_mcp` to see current tabs. Do **not** reuse an existing tab
   unless the user asked to — create a fresh one with `tabs_create_mcp`.
3. `navigate` to the app URL.

Tool calls per think-aloud move (the full loop lives in `think-aloud.md`; this
maps its moves onto MCP calls):

- **Scan** → `read_page` (structured text) or a screenshot via `computer`.
  Read only what a user would see; ignore DOM internals the persona cannot perceive.
- **Act** → `computer` (click at coordinates / type) or `find` to locate an
  element by description, then click. One action per step.
- **Observe** → another `read_page` or screenshot. Capture a screenshot for
  every SURPRISING result as evidence to cite in the report.

Cautions:
- Never trigger native `alert`/`confirm`/`prompt` dialogs — they freeze the
  extension. Avoid buttons that raise them; warn the user if a step requires one.
- If a tool call fails 2–3 times or the page will not load, stop and ask the
  user rather than looping.

Record concrete coordinates/labels acted on so a reader can reproduce the step.

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
