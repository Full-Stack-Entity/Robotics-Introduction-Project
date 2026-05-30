# Phase 5 DP Evaluation Summary

Date: 2026-05-30

## Run

- Command: `CHECKPOINT_NUM=100 pixi run robotwin-phase5-eval`
- Log root: `outputs/robotwin/logs/phase5_20260530-092044`
- Task config: `demo_clean_100`
- Checkpoint setting: `demo_clean_100`
- Expert data num: `100`
- Seed: `0`
- Checkpoint number: `100`
- Instruction type: `unseen`

The evaluated checkpoints were produced by the final Phase 4 quality profile:
`TRAIN_EPOCHS=100`, `CHECKPOINT_EVERY=100`, `BATCH_SIZE=16`,
`MAX_TRAIN_STEPS=null`, `MAX_VAL_STEPS=null`, and `USE_EMA=True`.

## Official Eval Results

| Task | Official result path | Success rate | Interpretation |
| --- | --- | ---: | --- |
| `grab_roller` | `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_100/demo_clean_100/2026-05-30 09:20:46/_result.txt` | 100/100 = 100% | Strong result; suitable for report and video. |
| `adjust_bottle` | `outputs/robotwin/artifacts/eval_result/adjust_bottle/DP/demo_clean_100/demo_clean_100/2026-05-30 09:49:09/_result.txt` | 71/100 = 71% | Good course result; substantially better than the previous 49%. |
| `place_burger_fries` | `outputs/robotwin/artifacts/eval_result/place_burger_fries/DP/demo_clean_100/demo_clean_100/2026-05-30 10:58:14/_result.txt` | 98/100 = 98% | Strong result; the full-dataloader EMA retraining fixed the earlier failure. |

The earlier limited-training checkpoints produced lower results:

| Task | Earlier result | Final result |
| --- | ---: | ---: |
| `grab_roller` | 90% | 100% |
| `adjust_bottle` | 49% | 71% |
| `place_burger_fries` | incomplete, 0 successes before interruption | 98% |

## Custom Single-Rollout Artifacts

| Task | Success | Viewer | Video |
| --- | --- | --- | --- |
| `grab_roller` | 1/1 | `outputs/robotwin/single_rollouts/grab_roller/demo_clean_100_seed0_ckpt100_20260530-094826/viewer.html` | `outputs/robotwin/single_rollouts/grab_roller/demo_clean_100_seed0_ckpt100_20260530-094826/episode0.mp4` |
| `adjust_bottle` | 1/1 | `outputs/robotwin/single_rollouts/adjust_bottle/demo_clean_100_seed0_ckpt100_20260530-105724/viewer.html` | `outputs/robotwin/single_rollouts/adjust_bottle/demo_clean_100_seed0_ckpt100_20260530-105724/episode0.mp4` |
| `place_burger_fries` | 1/1 | `outputs/robotwin/single_rollouts/place_burger_fries/demo_clean_100_seed0_ckpt100_20260530-121045/viewer.html` | `outputs/robotwin/single_rollouts/place_burger_fries/demo_clean_100_seed0_ckpt100_20260530-121045/episode0.mp4` |

Official eval results should be used as quantitative evidence in the report.
The custom single-rollout viewers and videos should be used for PPT/video
demonstration.

## Decision

Phase 5 is complete. The project should enter Phase 6: visual artifact
organization and result packaging for the report, PPT, and presentation video.
