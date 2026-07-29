# Personas

Scenarios are persona-driven. Each scenario is owned by one fictional user,
named with successive letters of the alphabet. The first persona is always
Alice.

## Ordered name list

Use these in order. Names alternate genders and mix cultural backgrounds to
encourage diverse personas. Stop at the requested scenario count (default 5,
up to 20).

1. alice
2. bob
3. carol
4. dave
5. erin
6. frank
7. grace
8. heidi
9. ivan
10. judy
11. kate
12. liam
13. mia
14. noah
15. olivia
16. priya
17. quinn
18. raj
19. sofia
20. tom

## Designing a good persona

A persona is a compact but concrete character. Keep it to a few lines, but make
every attribute *load-bearing* — it should plausibly change how the person uses
the tool.

Include:
- **Age and role** — anchors expectations and vocabulary (a CFO reads dashboards differently than a student).
- **Device / context** — iPad on a train, 27" monitor at a desk, SSH session on a server. Context drives layout and input constraints.
- **Expertise** — novice, intermediate, or expert *with this class of tool*. Novices expose onboarding gaps; experts expose efficiency gaps.
- **Mindset** — rushed, cautious, skeptical, distracted. Emotional state changes tolerance for friction.

## Designing a good goal

The goal is the concrete outcome the persona wants — not a feature to test.
State it as the user would think it, not as the developer would.

- Good: "Alice wants to upload her sales report and get it fact-checked."
- Weak: "Test the upload button."

One goal per scenario. The goal defines success and gives the think-aloud walk a
clear endpoint.

## Diversity across a set

When generating a set, deliberately spread across dimensions so the set as a
whole surfaces varied problems:

- Expertise: at least one clear novice and one clear expert.
- Device: mix mobile/touch and desktop/keyboard (for web); mix interactive and scripted use (for CLI).
- Goal type: creation, retrieval, correction/undo, configuration, first-run/onboarding.
- Mindset: at least one rushed and one cautious persona.

Two personas with identical attributes waste a scenario slot. Vary them.
