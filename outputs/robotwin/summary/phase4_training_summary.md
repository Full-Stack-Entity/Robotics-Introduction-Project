# Phase 4 DP Training Summary

Date: 2026-05-30

## Run

- Command: `TRAIN_EPOCHS=100 CHECKPOINT_EVERY=100 BATCH_SIZE=16 MAX_TRAIN_STEPS=null MAX_VAL_STEPS=null USE_EMA=True pixi run robotwin-phase4-train`
- Log root: `outputs/robotwin/logs/phase4_20260529-224707`
- Task config: `demo_clean_100`
- Expert episodes per task: `100`
- Seed: `0`
- GPU id: `0`
- Training profile: `TRAIN_EPOCHS=100`, `CHECKPOINT_EVERY=100`, `BATCH_SIZE=16`
- Full-dataloader settings: `MAX_TRAIN_STEPS=null`, `MAX_VAL_STEPS=null`
- Policy smoothing: `USE_EMA=True`
- Artifact root: `outputs/robotwin/artifacts`

This final quality run started at `2026-05-29 22:47:07 +0800` and the final
training log was updated at `2026-05-30 09:14:17 +0800`, for about 10.45 hours
of wall-clock time.

## Artifact Completeness

| Task | DP zarr | Zarr size | Final checkpoint | Checkpoint size | Train log | Process status |
| --- | --- | ---: | --- | ---: | --- | --- |
| `grab_roller` | `outputs/robotwin/artifacts/dp_data/grab_roller-demo_clean_100-100.zarr` | 879M | `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_100-100-0/100.ckpt` | 1.5GB | `outputs/robotwin/logs/phase4_20260529-224707/grab_roller_train.log` | existing zarr reused |
| `adjust_bottle` | `outputs/robotwin/artifacts/dp_data/adjust_bottle-demo_clean_100-100.zarr` | 1.2G | `outputs/robotwin/artifacts/checkpoints/adjust_bottle-demo_clean_100-100-0/100.ckpt` | 1.5GB | `outputs/robotwin/logs/phase4_20260529-224707/adjust_bottle_train.log` | existing zarr reused |
| `place_burger_fries` | `outputs/robotwin/artifacts/dp_data/place_burger_fries-demo_clean_100-100.zarr` | 2.4G | `outputs/robotwin/artifacts/checkpoints/place_burger_fries-demo_clean_100-100-0/100.ckpt` | 1.5GB | `outputs/robotwin/logs/phase4_20260529-224707/place_burger_fries_train.log` | existing zarr reused |

All three tasks reached the configured 100 epochs and saved `100.ckpt`.

## Training Loss Evidence

The structured DP logs under `outputs/robotwin/artifacts/dp_data/outputs/`
show the following final epoch-99 records:

| Task | Final global step | Final train loss | Final val loss | Notes |
| --- | ---: | ---: | ---: | --- |
| `grab_roller` | 58199 | 0.00204 | 0.00861 | Complete full-dataloader run with EMA. |
| `adjust_bottle` | 87299 | 0.00135 | 0.00212 | Complete full-dataloader run with EMA. |
| `place_burger_fries` | 149199 | 0.00110 | 0.00138 | Complete full-dataloader run with EMA. |

Compared with the earlier capped run, this profile removes the per-epoch
`MAX_TRAIN_STEPS=100` limit, uses the complete dataloader, and enables EMA.
It produced the final checkpoints used by Phase 5.

## Limitations

- Training loss is not a success-rate metric. Official task success is reported
  in `outputs/robotwin/summary/phase5_eval_summary.md`.
- The script did not sample peak VRAM usage. The safe claim is that the final
  `BATCH_SIZE=16` full-dataloader EMA profile completed on the available 12GB GPU.

## Decision

Phase 4 is complete with final checkpoints at `100.ckpt`. Phase 5 should use:

```bash
CHECKPOINT_NUM=100 pixi run robotwin-phase5-eval
```
