---
description: Run a persona-driven, think-aloud UX test on a web app or CLI tool
argument-hint: [tool URL or path] [optional: N scenarios]
---

Run the **better-ux** usability-testing workflow.

Follow the skill instructions at `${CLAUDE_PLUGIN_ROOT}/skills/better-ux/SKILL.md`
exactly — start with Phase 1 (Intake), then Scenarios, Execution (think-aloud),
and Distillation. Consult its `references/` and `assets/` as directed there.

Target and any options the user provided: $ARGUMENTS

If no target was provided, begin Phase 1 by asking how to run the tool and where
its intended behavior is described.
