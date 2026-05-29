# Task Plan: Robotics Simulation Feasibility Review

## Goal
Assess whether a SAPIEN-based required robotics simulation plus a RoboTwin2.0-based embodied-AI extension is feasible for the robotics introduction course deliverables.

## Phases
- [x] Phase 1: Setup and identify local materials
- [x] Phase 2: Extract course requirements and local RoboTwin evidence
- [x] Phase 3: Verify current SAPIEN and RoboTwin2.0 facts from primary sources
- [x] Phase 4: Synthesize feasibility, risks, and recommended next steps

## Key Questions
1. Do the proposed tasks cover the mandatory point control and pose/trajectory control requirements?
2. Can SAPIEN support a lightweight, visually demonstrable traditional robotics workflow?
3. Can RoboTwin2.0 be used for fresh data generation, training, evaluation, and rollout display without overloading the course timeline?
4. What should be treated as core deliverable versus optional extension?

## Decisions Made
- Use SAPIEN as the primary simulator for required deterministic motion-control demonstrations.
- Treat RoboTwin2.0 as an extension/demo layer, not as the grading-critical core.
- Reuse the adjacent RoboTwin `pixi` environment for extension work where possible.
- Do not use previous ACT training artifacts as final course results; use them only as evidence that the local RoboTwin stack has been made runnable before.
- Prefer one policy family across tasks: DP first, DP3 only as an optional higher-risk branch.
- Interpret "single model across multiple tasks" conservatively as the same model family with per-task checkpoints; true multi-task single-checkpoint training is out of scope unless explicitly promoted later.
- Add custom single-rollout visualization in addition to official RoboTwin evaluation scripts.
- Use online/interactive visualization when stable; otherwise export mp4 videos for both SAPIEN and RoboTwin demonstrations.

## Errors Encountered
- Current project folder is not a git repository; record status as filesystem-only for now.
- No `scripts/codex_hook_emulation.py` exists in this folder, so session-start hook emulation was skipped.
- Tried to read `../RoboTwin-Project/README.md`, but the correct upstream README is `../RoboTwin-Project/RoboTwin/README.md`.

## Status
**Completed** - `TASKS.md` now reflects fresh DP training, leaderboard-based task selection, and visualization/rollout deliverables.
