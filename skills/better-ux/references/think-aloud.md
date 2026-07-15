# The think-aloud technique

Think-aloud is a usability method where the user narrates their thoughts while
attempting a task. The value is in the *reasoning*, not just the clicks: it
exposes the gap between what the interface implies and what actually happens.

When executing a scenario, stay in the persona's head and narrate continuously.

## Use a less capable model as the "user"

Model choice is a usability variable, not just a cost decision. A frontier model
is too good at this test: it infers hidden affordances, guesses the one correct
command, silently recovers from bad errors, and reads meaning into ambiguous
labels — so it *reaches the goal anyway* and the interface looks better than it
is. Real users do none of that.

Run the execution phase with a deliberately weaker model (Haiku, or Sonnet).
A weaker model:
- takes labels and messages literally, exposing wording that only "works" if the reader is clever;
- gets genuinely stuck where affordances are missing, instead of brute-forcing past them;
- makes the plausible-but-wrong guesses a real novice makes, surfacing unforgiving error paths.

The friction a weaker model hits is a lower bound on the friction real users hit.
Keep scenario design and the final distillation on the stronger model (they
benefit from breadth and judgment); move only the per-scenario walkthrough to the
weaker model. In practice, spawn each walkthrough as a subagent with an explicit
model override so the persona's capability is fixed and reproducible across runs.

## The per-step loop

For every single step, walk these five moves explicitly and record them:

1. **Scan** — What does the persona actually see right now? List only what is
   visible: labels, buttons, headings, prompts, output lines. Do not reference
   anything off-screen or any internal knowledge.

2. **Expect** — *Before acting*, state the hypothesis: "I think clicking X will
   do Y, because the label says Z." This is the testable prediction. Naming it
   first is what makes the next observation meaningful.

3. **Act** — Take exactly one action. One click, one field filled, one command
   run, one link followed. One action per step keeps cause and effect clear.

4. **Observe** — Record what actually happened: the new screen, the toast, the
   error, the stdout, the exit code. Capture a screenshot for web surprises.

5. **Judge** — Compare observation to expectation. Mark **EXPECTED** or
   **SURPRISING**, assign a severity, and note the felt experience (confusion,
   relief, annoyance, delight).

## The golden rule: only use visible clues

The persona knows nothing the interface has not shown them. Do not use developer
knowledge — hidden keyboard shortcuts, the "right" menu, the API — unless the UI
advertises it. Acting only on visible affordances is exactly what reveals
missing labels, buried features, and misleading cues.

If the persona cannot find how to proceed, that is a finding — record where they
got stuck and what they looked for, then either try a plausible fallback or have
the persona give up (also a valid, informative outcome).

## What counts as "surprising"

Mark a step SURPRISING when reality diverges from a *reasonable* expectation:

- The action did nothing, or did something different than the label implied.
- An error appeared with no clear cause or next step.
- The result required knowledge the persona did not have.
- A destructive action happened without confirmation.
- The system was silent when feedback was expected (no spinner, no confirmation).
- A default value or pre-selection was wrong for this persona.
- The happy path worked but took far more steps than the persona expected.

Delight is also worth recording (a helpful default, a clear empty state) — the
distillation step should protect what works, not just fix what breaks.

## Severity rubric

Assign each finding a severity to drive ranking later:

- **Critical** — blocks the goal entirely, or causes data loss / irreversible harm.
- **High** — the persona can eventually succeed but only via confusion, retries, or luck.
- **Medium** — noticeable friction or inconsistency that slows or annoys, but is worked around.
- **Low** — cosmetic, minor wording, or nice-to-have polish.

## Judging against intent

"Surprising" is judged against what the tool *claims* to do (the description
source gathered in intake), not against personal preference. Before ranking a
finding, check: does this contradict the tool's stated purpose or a reasonable
user's mental model? If yes, it is a real finding. If it is merely a preference,
mark it Low or drop it.
