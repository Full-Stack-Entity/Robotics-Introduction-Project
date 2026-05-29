# Phase 4 DP Training Summary

Date: 2026-05-29

## Run

- Command: `pixi run robotwin-phase4-train`
- Log root: `outputs/robotwin/logs/phase4_20260529-144921`
- Task config: `demo_clean_100`
- Expert episodes per task: `100`
- Seed: `0`
- GPU id: `0`
- Training profile: `TRAIN_EPOCHS=200`, `CHECKPOINT_EVERY=200`, `BATCH_SIZE=32`
- Bounded training: `MAX_TRAIN_STEPS=100`, `MAX_VAL_STEPS=20`, `USE_EMA=False`
- Artifact root: `outputs/robotwin/artifacts`

The run started at `2026-05-29 14:49:21 +0800` and the final training log was
updated at `2026-05-29 18:12:32 +0800`, for about 3.4 hours of wall-clock time.

## Artifact Completeness

| Task | DP zarr | Zarr size | Checkpoint | Checkpoint size | Train log | Process status |
| --- | --- | ---: | --- | ---: | --- | --- |
| `grab_roller` | `outputs/robotwin/artifacts/dp_data/grab_roller-demo_clean_100-100.zarr` | 879M | `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_100-100-0/200.ckpt` | 1.16GB | `outputs/robotwin/logs/phase4_20260529-144921/grab_roller_train.log` | existing zarr reused |
| `adjust_bottle` | `outputs/robotwin/artifacts/dp_data/adjust_bottle-demo_clean_100-100.zarr` | 1.2G | `outputs/robotwin/artifacts/checkpoints/adjust_bottle-demo_clean_100-100-0/200.ckpt` | 1.16GB | `outputs/robotwin/logs/phase4_20260529-144921/adjust_bottle_train.log` | processed 100/100 episodes |
| `place_burger_fries` | `outputs/robotwin/artifacts/dp_data/place_burger_fries-demo_clean_100-100.zarr` | 2.4G | `outputs/robotwin/artifacts/checkpoints/place_burger_fries-demo_clean_100-100-0/200.ckpt` | 1.16GB | `outputs/robotwin/logs/phase4_20260529-144921/place_burger_fries_train.log` | processed 100/100 episodes |

All three tasks reached `Training epoch 199` and `Validation epoch 199`, which
corresponds to the configured 200 epochs.

## Training Loss Evidence

The structured DP logs under `outputs/robotwin/artifacts/dp_data/outputs/`
show the following final epoch-199 records:

| Task | Initial train loss | Final train loss | Final val loss | Notes |
| --- | ---: | ---: | ---: | --- |
| `grab_roller` | 1.13498 | 0.00899 | 0.00857 | Structured log includes lines from the earlier interrupted run because the Hydra output directory was reused; the final record and checkpoint are from the completed 200-epoch run. |
| `adjust_bottle` | 1.13898 | 0.01005 | 0.01016 | Clean 200-epoch structured log. |
| `place_burger_fries` | 1.12718 | 0.01116 | 0.00976 | Clean 200-epoch structured log. |

The loss curves indicate that optimization converged to a low reconstruction /
diffusion training loss for all three tasks. This is sufficient evidence that
Phase 4 training completed and produced usable checkpoints.

## Limitations

- Training loss is not a success-rate metric. It only proves that the imitation
  objective optimized normally.
- Final task performance must be determined by Phase 5 official RoboTwin eval.
- The script did not sample peak VRAM usage. The safe claim is that the
  200-epoch profile with `BATCH_SIZE=32` completed on the available 12GB GPU.
- The custom single-rollout videos in Phase 5 should be used for PPT/video
  demonstration, while official eval success rates should be used for the
  quantitative report.

## Decision

Phase 4 is complete. The project is ready to enter Phase 5 with:

```bash
pixi run robotwin-phase5-eval
```

The Phase 5 script now defaults to `CHECKPOINT_NUM=200`, matching the Phase 4
checkpoints produced here.
