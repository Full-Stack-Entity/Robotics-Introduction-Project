# Phase 6 Visual and Result Artifact Index

Date: 2026-05-30

This index freezes the report/PPT/video-facing artifact paths after the final
Phase 4 quality retraining and Phase 5 evaluation. Large generated videos,
checkpoints, zarr files, and eval directories remain local generated artifacts;
this file records where to find and how to use them.

## Evidence Boundary

- Quantitative task performance: use official RoboTwin eval success rates.
- Presentation evidence: use SAPIEN videos, RoboTwin expert demonstrations, and
  custom single-rollout viewers/videos.
- Training loss: use only as optimization evidence, not as task success.

## SAPIEN Required-Control Artifacts

| Task | Video | Plot | Keyframes | CSV | Suggested use |
| --- | --- | --- | --- | --- | --- |
| Six-point Cartesian control | `outputs/sapien/videos/six_points.mp4` | `outputs/sapien/plots/six_points_trajectory.png` | `outputs/sapien/frames/six_points/key_*.png` | `outputs/sapien/logs/six_points_trajectory.csv` | Report trajectory-planning section; PPT clip for point-to-point control. |
| Figure-eight end-effector trajectory | `outputs/sapien/videos/figure_eight.mp4` | `outputs/sapien/plots/figure_eight_trajectory.png` | `outputs/sapien/frames/figure_eight/key_*.png` | `outputs/sapien/logs/figure_eight_trajectory.csv` | Report continuous trajectory tracking; video clip after six-point task. |
| Ellipse end-effector trajectory | `outputs/sapien/videos/ellipse.mp4` | `outputs/sapien/plots/ellipse_trajectory.png` | `outputs/sapien/frames/ellipse/key_*.png` | `outputs/sapien/logs/ellipse_trajectory.csv` | Secondary continuous trajectory example; useful for comparing planned paths. |

SAPIEN browser replay:

```text
outputs/sapien/viewer.html
```

SAPIEN summary:

```text
outputs/sapien/summary.md
```

## RoboTwin Expert Demonstrations

These clips show the generated expert data used for DP training. They should be
described as data-generation examples, not learned policy rollouts.

| Task | Expert demo video | Data summary use |
| --- | --- | --- |
| `grab_roller` | `outputs/robotwin/artifacts/data/grab_roller/demo_clean_100/video/episode0.mp4` | Demonstrates dual-arm grasp/lift expert behavior. |
| `adjust_bottle` | `outputs/robotwin/artifacts/data/adjust_bottle/demo_clean_100/video/episode0.mp4` | Demonstrates bottle adjustment expert behavior. |
| `place_burger_fries` | `outputs/robotwin/artifacts/data/place_burger_fries/demo_clean_100/video/episode0.mp4` | Demonstrates semantic pick-and-place expert behavior. |

Data-generation summary:

```text
outputs/robotwin/summary/phase3_data_summary.md
```

## RoboTwin Training Artifacts

Final training profile:

```bash
TRAIN_EPOCHS=100 \
CHECKPOINT_EVERY=100 \
BATCH_SIZE=16 \
MAX_TRAIN_STEPS=null \
MAX_VAL_STEPS=null \
USE_EMA=True \
pixi run robotwin-phase4-train
```

Final checkpoints:

| Task | Checkpoint |
| --- | --- |
| `grab_roller` | `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_100-100-0/100.ckpt` |
| `adjust_bottle` | `outputs/robotwin/artifacts/checkpoints/adjust_bottle-demo_clean_100-100-0/100.ckpt` |
| `place_burger_fries` | `outputs/robotwin/artifacts/checkpoints/place_burger_fries-demo_clean_100-100-0/100.ckpt` |

Training visual/table artifacts:

```text
outputs/robotwin/summary/training_loss_curves.png
outputs/robotwin/summary/training_loss_epoch_summary.csv
outputs/robotwin/summary/phase4_training_summary.md
```

## RoboTwin Official Evaluation Results

Final evaluation command:

```bash
CHECKPOINT_NUM=100 pixi run robotwin-phase5-eval
```

| Task | Official success rate | Result file | Report interpretation |
| --- | ---: | --- | --- |
| `grab_roller` | 100/100 = 100% | `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_100/demo_clean_100/2026-05-30 09:20:46/_result.txt` | Strong and stable result. |
| `adjust_bottle` | 71/100 = 71% | `outputs/robotwin/artifacts/eval_result/adjust_bottle/DP/demo_clean_100/demo_clean_100/2026-05-30 09:49:09/_result.txt` | Good course result; improved from the earlier capped-training run. |
| `place_burger_fries` | 98/100 = 98% | `outputs/robotwin/artifacts/eval_result/place_burger_fries/DP/demo_clean_100/demo_clean_100/2026-05-30 10:58:14/_result.txt` | Strong final result; full-dataloader EMA retraining fixed the earlier failure. |

Result summaries:

```text
outputs/robotwin/summary/phase5_eval_summary.md
outputs/robotwin/summary/final_success_rates.md
outputs/robotwin/summary/final_success_rates.csv
```

## RoboTwin Custom Single-Rollout Artifacts

These artifacts are for PPT/video demonstration. They should not replace the
official eval table when reporting quantitative success.

| Task | Viewer | Video | Single rollout result |
| --- | --- | --- | --- |
| `grab_roller` | `outputs/robotwin/single_rollouts/grab_roller/demo_clean_100_seed0_ckpt100_20260530-094826/viewer.html` | `outputs/robotwin/single_rollouts/grab_roller/demo_clean_100_seed0_ckpt100_20260530-094826/episode0.mp4` | 1/1 success |
| `adjust_bottle` | `outputs/robotwin/single_rollouts/adjust_bottle/demo_clean_100_seed0_ckpt100_20260530-105724/viewer.html` | `outputs/robotwin/single_rollouts/adjust_bottle/demo_clean_100_seed0_ckpt100_20260530-105724/episode0.mp4` | 1/1 success |
| `place_burger_fries` | `outputs/robotwin/single_rollouts/place_burger_fries/demo_clean_100_seed0_ckpt100_20260530-121045/viewer.html` | `outputs/robotwin/single_rollouts/place_burger_fries/demo_clean_100_seed0_ckpt100_20260530-121045/episode0.mp4` | 1/1 success |

## Recommended Use In Deliverables

| Deliverable | Use these artifacts |
| --- | --- |
| LaTeX report | SAPIEN plots, `final_success_rates.md`, `training_loss_curves.png`, official eval result paths. |
| PPT | SAPIEN videos, one expert demo per RoboTwin task, one custom rollout per RoboTwin task, final success-rate table. |
| Presentation video | Follow `outputs/video_segment_plan.md`; use official eval only as narrated quantitative evidence. |

