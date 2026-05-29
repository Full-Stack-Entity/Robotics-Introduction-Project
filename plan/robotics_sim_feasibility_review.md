# Robotics Simulation Feasibility Review

Status: updated after leaderboard-based RoboTwin task screening.

## Verdict

The overall route is feasible and well aligned with the course grading requirements if it is split into two layers:

1. Required robotics layer: SAPIEN deterministic manipulator simulation for six-point point control, figure-eight trajectory, and elliptical trajectory.
2. Extension embodied-AI layer: RoboTwin2.0 fresh data generation, one diffusion-policy family, selected tasks, per-task training/evaluation, and short rollout videos.
3. Visualization layer: prioritize online/interactive playback for both SAPIEN and RoboTwin; export mp4 videos as the stable fallback.

The key constraint is scope control. RoboTwin should not replace the required traditional robotics simulation; it should be framed as an extension that demonstrates the transition from programmed control to data-driven embodied intelligence.

## Course Fit

The course PDF requires:

- Platform/environment description.
- Robot trajectory planning design.
- Control process.
- Simulation effects.
- Pseudocode.
- Result analysis.
- References and formatting.
- Video with the student on camera and clear explanation.

The SAPIEN layer directly satisfies the required control part. RoboTwin adds stronger project depth, but should be presented after the required trajectory-control content.

## Visualization Requirement

Visualization is part of the acceptance criteria, not a cosmetic add-on:

- SAPIEN required tasks should support interactive/online preview if stable.
- If SAPIEN interactive visualization is unstable, each required task must export mp4 video plus key frames.
- RoboTwin official eval scripts remain the quantitative evaluation source.
- A separate custom single-rollout script should run one trained model rollout for each selected task.
- The custom RoboTwin rollout script should prioritize online/interactive playback; if that is not stable, it must export one mp4 per task.
- The report must distinguish official evaluation results from custom demonstration rollouts.

## RoboTwin Fresh-Training Route

Do not use previous ACT checkpoints or videos as final results. Existing RoboTwin work should only be cited internally as evidence that the local environment and dependency stack have been made runnable.

Recommended interpretation of "single model across multiple tasks":

- Same model family: Diffusion Policy / DP.
- Separate per-task checkpoints.
- Shared report structure and shared command pipeline across tasks.

True multi-task single-checkpoint training is a separate engineering problem and is not recommended for this course deadline unless it becomes an explicit later goal.

## Policy Choice

### Recommended Default: DP

DP is the safer course route:

- Uses RGB head-camera observations plus robot state.
- Does not require point-cloud data collection.
- Has a straightforward script chain in the local RoboTwin checkout:
  - `policy/DP/process_data.sh`
  - `policy/DP/train.sh`
  - `policy/DP/eval.sh`
- Default config uses ResNet18 + diffusion UNet, 600 epochs, and batch size 128.

The leaderboard shows DP can work well on selected Easy/demo_clean tasks, but DP is weak on most Hard/demo_randomized evaluations. Treat randomized evaluation as a robustness stress test, not the main success target.

### Optional Higher-Risk Branch: DP3

DP3 has much better leaderboard performance on many tasks, but it is riskier:

- Requires point-cloud data (`data_type.pointcloud: true`).
- Default config is heavier: batch size 256, 3000 epochs, point-cloud encoder.
- May need batch-size and training-step tuning on a 12GB RTX 4080 Laptop GPU.

Use DP3 only after a one-task smoke test proves that point-cloud data collection, preprocessing, training, and evaluation are stable.

## Recommended DP Task Set

Primary 3-task set:

| Task | DP Easy | DP Hard | Why use it |
| --- | ---: | ---: | --- |
| `grab_roller` | 98% | 0% | Strongest DP Easy score; bimanual grasp-and-lift is visually clear. |
| `adjust_bottle` | 97% | 0% | Strong DP Easy score; simple pick/adjust behavior; good reliability candidate. |
| `place_burger_fries` | 72% | 0% | Visually rich dual-arm pick-place task; good for PPT/video even if not top score. |

Optional 4th/5th tasks:

| Task | DP Easy | DP Hard | Why use it |
| --- | ---: | ---: | --- |
| `stack_bowls_two` | 61% | 0% | Clear object-manipulation story; easier than three-bowl stacking. |
| `shake_bottle_horizontally` | 59% | 18% | Best DP Hard among the screened tasks and visually dynamic, but lower Easy margin. |
| `click_alarmclock` | 61% | 5% | Short, simple backup task if training/evaluation time is tight. |

Avoid as primary DP success demos:

- `lift_pot`: DP Easy 39%, despite being visually meaningful.
- `beat_block_hammer`: DP Easy 42%; useful historically, but weaker than the selected tasks for DP.
- Any task whose main success claim depends on `demo_randomized` DP performance.

## DP3 Candidate Set

If DP3 one-task smoke passes, the best-looking DP3 candidate set is:

| Task | DP3 Easy | DP3 Hard | Notes |
| --- | ---: | ---: | --- |
| `shake_bottle_horizontally` | 100% | 25% | Strong and visually dynamic. |
| `handover_mic` | 100% | 3% | High Easy score; handover is semantically clear. |
| `adjust_bottle` | 99% | 3% | Very reliable Easy task. |
| `grab_roller` | 98% | 2% | Strong bimanual lift. |
| `shake_bottle` | 98% | 19% | Good dynamic-action candidate. |

DP3 is attractive if time allows, but DP remains the recommended default because it has fewer data and preprocessing requirements.

## Data Scale

The leaderboard baseline uses 50 `demo_clean` demonstrations per task. Therefore 100-200 demonstrations per selected task is a reasonable course-scale plan, not an undersized plan.

Recommended scale:

- Smoke stage: 5-10 demos for one selected task to test data generation, DP preprocessing, training start, and evaluation path.
- First formal stage: 100 demos for `grab_roller`, `adjust_bottle`, and `place_burger_fries`.
- Optional extension: expand the best 1-2 tasks to 200 demos if training/evaluation finishes early.
- Evaluation: 20-50 rollouts per task for course reporting, not necessarily full 100-rollout leaderboard reproduction.

## Expected Timeline

As of 2026-05-28, the deadline is 2026-06-08 24:00. This leaves about 11 days.

Suggested schedule:

- Day 1-2: Implement and record SAPIEN required-control layer.
- Day 2-3: RoboTwin DP smoke on `grab_roller`.
- Day 3-5: Generate 100 demos each for the selected 3 tasks.
- Day 5-8: DP preprocessing and training; tune batch size/epochs only if needed.
- Day 8-9: Evaluation, rollout video selection, result tables.
- Day 9-11: LaTeX report, PPT, and video script.

## Main Risks

- DP randomized/Hard success is low, so do not promise robust generalization.
- 3-5 tasks with 200 demos each can become expensive if data generation fails often or training is run with default 600 epochs for every task.
- DP3 may look better on leaderboard but has higher point-cloud and training risk.
- The current course project folder is not a git repository; if implementation begins here, initialize git or maintain clear file snapshots.
- Current RoboTwin checkout has existing local modifications; preserve them unless we intentionally branch or copy the project.

## Recommended Next Step

Proceed with the plan, but stage it conservatively:

1. Finish the SAPIEN required-control simulation first.
2. Run one fresh DP smoke on `grab_roller` with a tiny demo count.
3. If smoke passes, generate/train the 3-task DP set: `grab_roller`, `adjust_bottle`, `place_burger_fries`.
4. Implement official eval plus custom single-rollout visualization for the 3 trained tasks.
5. Add `stack_bowls_two` or `shake_bottle_horizontally` only if the 3-task set finishes with usable videos.

## Source Links

- Course PDF: `2026机器人学导论实验——课程报告说明.pdf`
- RoboTwin official leaderboard: https://robotwin-platform.github.io/leaderboard
- RoboTwin official repository README in local checkout: `../RoboTwin-Project/RoboTwin/README.md`
- RoboTwin 2.0 paper: https://arxiv.org/abs/2506.18088
- SAPIEN documentation: https://sapien-sim.github.io/docs/
