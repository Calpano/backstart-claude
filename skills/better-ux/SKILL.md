---
name: better-ux
description: This skill should be used when the user asks to "UX test" or "usability test" a web app or CLI tool, "run a UX review", "test the UX", "do a think-aloud test", "evaluate the usability of" a tool, or mentions "better-ux". It brainstorms persona-driven scenarios, executes them with the think-aloud technique, and distills a ranked list of concrete UX improvements.
version: 0.1.0
---

# better-ux

Run structured usability tests on a web app or a CLI tool. The skill acts as a
panel of fictional users who each pursue a real goal, narrate their reasoning
out loud (think-aloud), and record every assumption, action, and surprise. The
run ends with a ranked, actionable list of improvements backed by evidence.

## Workflow overview

The skill runs in four phases. Complete them in order; skip a phase only when
its output already exists and is sufficient.

1. **Intake** — learn how to run the tool and where its intended behavior is described.
2. **Scenarios** — brainstorm persona-driven scenarios into `scenarios/`.
3. **Execution** — walk each scenario with the think-aloud technique, one report per run.
4. **Distillation** — scan the run's reports and produce a ranked improvement list.

All artifacts are written as AsciiDoc (`.adoc`). The layout created in the
target project (the tool's working directory, not the skill directory) is:

```
scenarios/
  scenario-alice.adoc
  scenario-bob.adoc
reports/
  2026-07-21-alice-001.adoc
  2026-07-21-bob-001.adoc
  improvements-001.adoc
```

## Phase 1: Intake

Before any testing, establish two things by asking the user (ask both together;
do not over-question). Record the answers — they are reused in every report.

**1. How is the tool run?**
- Web app with a live URL → capture the URL.
- Web app needing a dev server → capture the launch command (e.g. `npm run dev`) and the resulting local URL.
- CLI tool → capture the invocation path or command, plus any install/build step needed first.

**2. Where is the tool's intended behavior described?**
This is the "source of truth" for judging whether behavior is correct. Good sources:
- Web: the product homepage, marketing/docs site, or in-app help.
- CLI: `--help` / `-h` output, `man` page.
- Either: a `README`, `CHANGELOG`, or design doc.

Read the description source before writing scenarios — scenarios must reflect
what the tool *claims* to do, so that "surprising" behavior can be judged against intent.

Determine the tool **type** (`web`, `cli`, or `both`); it selects the execution
approach in Phase 3. For a **web** (or **both**) tool, also confirm now that a
browser-automation driver is available. If none is installed, offer to install
**chrome-devtools-mcp** before proceeding — see `references/driving.md` for the
one-line install command and the fallback order.

## Phase 2: Scenario brainstorming

Create the `scenarios/` directory if absent. **First check what already exists** —
if enough scenarios are present for the requested count, skip to Phase 3.

Ask the user how many scenarios to generate. **Default is 5; up to 20 is normal.**

Assign each scenario a persona named with successive alphabet letters: the first
is always `alice`, then `bob`, `carol`, `dave`, and so on. The scenario file is
`scenarios/scenario-<name>.adoc` (e.g. `scenario-alice.adoc`). See
`references/personas.md` for the ordered name list and persona-design guidance.

Each scenario is short and contains:
- **Persona** — name, age, role, and salient context/device (e.g. "Alice is a 25-year-old marketing student using an iPad").
- **Goal** — the concrete outcome the persona wants (e.g. "Alice wants to upload her sales report for fact-checking").
- **Starting point** — where the persona begins (the URL, or the shell).
- **Success criteria** — the observable end state that means the goal was met.

Aim for *diversity*: vary expertise (novice ↔ expert), device/context, goals,
and emotional state (rushed, cautious, skeptical). Diverse personas surface
diverse UX problems. Copy `assets/scenario-template.adoc` as the starting
structure for each file.

## Phase 3: Execution (think-aloud)

Pick a **run id** for this pass: a zero-padded counter (`001`, `002`, …) shared
by every report in the pass. Determine the next id by scanning `reports/` for the
highest existing `improvements-NNN.adoc` / `*-NNN.adoc` and adding one.

Walk **every** scenario, producing **at least one report per scenario**. Report
filename pattern: `reports/<ISO-date>-<persona>-<runid>.adoc`, e.g.
`reports/2026-07-21-alice-001.adoc` (ISO date = today, `YYYY-MM-DD`).

> Naming note: report files use the `.adoc` extension (AsciiDoc), not `.doc`,
> so they render consistently with scenarios and improvements.

**Run the walkthrough with a less capable model.** A highly capable model powers
straight through confusing UI that would stop a real person, which *hides* the
very friction this skill exists to find. Execute the think-aloud walkthrough with
a deliberately weaker model (Haiku, or Sonnet) so it stumbles where real users
stumble. Prefer running each scenario's execution as a subagent with an explicit
model override (e.g. the Agent tool with `model: "haiku"`), passing the persona,
goal, and the think-aloud rules; the stronger model then handles only scenario
design (Phase 2) and distillation (Phase 4). If subagents are unavailable,
recommend the user switch the session model to Haiku/Sonnet for the execution
phase. See `references/think-aloud.md` for why weaker-model execution yields
better UX findings.

**Isolate each persona's data.** Personas must not see each other's writes.
When scenarios run in parallel (or even sequentially) against one shared mutable
store, one persona's rows contaminate another's observations — a "surprising"
duplicate or unexpected row may be another persona's doing, not a real defect.
Give each persona an isolated copy of the tool's state, and restore the target
to its original state when the run ends (never leave the user's real data
mutated). Snapshot the initial state first. See `references/driving.md` →
"Isolating persona state" for concrete CLI and web recipes. If true isolation is
impossible, run personas sequentially, reset state between them, and record in
each report that state may have carried over.

Apply the think-aloud loop for each step, narrating reasoning explicitly:

1. **Scan** — observe the current UI / CLI output as the persona would.
2. **Expect** — state, before acting, what the persona believes will happen and why (this is the testable hypothesis).
3. **Act** — take one action: click, type, run a command, follow a link.
4. **Observe** — record what actually happened.
5. **Judge** — mark it **expected** or **surprising**, and note friction, confusion, or delight.

Stay in the persona's head: use only clues visible on screen or in output as
triggers for action. Do not use developer knowledge the persona would not have —
that is what exposes real usability gaps.

Record in the report, per step: the assumption/expectation, the clue that
triggered the action, the action, the result, and the expected/surprising
verdict with a severity. Copy `assets/report-template.adoc` as the structure.

**Driving the tool** (details in `references/driving.md`):
- **Web** — use the claude-in-chrome MCP: call `tabs_context_mcp` first, open a tab, then `navigate`, `read_page`, `computer`/`find` to act, and screenshots to evidence surprises. Start a dev server first if intake specified one.
- **CLI** — use Bash: run the command as the persona would, capture stdout/stderr/exit codes, and treat cryptic errors, missing help, or bad defaults as UX findings.

## Phase 4: Distillation

After all scenarios in the run are executed, read **all** reports for that run id
and synthesize one ranked improvement list: `reports/improvements-<runid>.adoc`
(e.g. `improvements-001.adoc`).

Each improvement is **actionable and ranked**. For each entry provide:
- A rank and a severity (Critical / High / Medium / Low).
- A one-line problem statement.
- **Evidence** — which persona(s)/report(s) and step surfaced it (cross-reference filenames).
- A **concrete recommendation** — what to change, specifically.

Rank by impact × frequency: problems that blocked a goal, or that recurred
across multiple personas, rank highest. Merge duplicate findings and cite every
report they came from. Copy `assets/improvements-template.adoc` as the structure.

Close by summarizing the top 3 findings to the user in chat.

## Additional resources

### Reference files
- **`references/personas.md`** — ordered persona name list (alice…) and how to design diverse, realistic personas and goals.
- **`references/think-aloud.md`** — the think-aloud method in depth: how to narrate, what counts as "surprising", and severity rubric.
- **`references/driving.md`** — concrete recipes for driving web apps (claude-in-chrome MCP) and CLI tools (Bash), including dev-server startup.

### Assets (templates to copy)
- **`assets/scenario-template.adoc`** — a single scenario.
- **`assets/report-template.adoc`** — one think-aloud run report.
- **`assets/improvements-template.adoc`** — the ranked improvement list.
