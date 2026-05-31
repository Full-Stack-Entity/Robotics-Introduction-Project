# Command Log

This file records reproducible commands for the course simulation project.

## 2026-05-28 Phase 0 Environment Verification

Working directory:

```bash
cd /home/robotics/桌面/Embodied-AI/Robotics-Introduction-Project
```

Environment sync:

```bash
pixi install --frozen --no-progress -v
```

Smoke tests:

```bash
pixi run python-smoke
pixi run sapien-import-smoke
pixi run ffmpeg-video-smoke
pixi run dp-import-smoke
pixi run robotwin-core-import-smoke
pixi run sapien-render-smoke
pixi run write-env-report
```

Observed result:

- Python, SAPIEN, MPLib, PyTorch imports passed.
- FFmpeg `libx264` video backend passed.
- RoboTwin DP imports passed.
- RoboTwin core task imports passed for `grab_roller`, `adjust_bottle`, and `place_burger_fries`.
- SAPIEN render smoke printed `Render Well`.
- Environment report was written to `outputs/environment.md`.

Notes:

- `yourdfpy` is installed as a PyPI dependency (`0.0.60`) to avoid conda-side `trimesh==4.12.2` pinning conflicts.
- `pytorch3d` is currently optional for this smoke path; `robotwin-core-import-smoke` reports it as missing but exits successfully.

## 2026-05-29 Phase 1 SAPIEN Basic Simulation

Working directory:

```bash
cd /home/robotics/桌面/Embodied-AI/Robotics-Introduction-Project
```

Fast smoke test:

```bash
pixi run sapien-basic-smoke
```

Browser live preview:

```bash
pixi run sapien-basic-live
```

The command prints a local URL such as `http://127.0.0.1:8001`; open it in a browser while the task is running.

Full artifact generation:

```bash
pixi run sapien-basic-tasks
```

Artifact checks:

```bash
pixi run python -m py_compile scripts/sapien/*.py
```

Observed result:

- The visual robot was upgraded from a simple schematic arm to the RoboTwin `franka-panda` URDF mesh.
- Control path: `Cartesian target -> MPlib IK -> Franka Panda qpos -> SAPIEN URDF rendering`.
- `six_points`: 176 frames, max position error about `0.00001033 m`.
- `figure_eight`: 180 frames, max position error about `0.00001016 m`.
- `ellipse`: 180 frames, max position error about `0.00001016 m`.
- Browser live preview was verified with the local HTTP page.
- Offline replay page was localized to Chinese: `outputs/sapien/viewer.html`.
- Videos were written to `outputs/sapien/videos/`.
- Keyframes were written to `outputs/sapien/frames/`.
- Trajectory CSV logs were written to `outputs/sapien/logs/`.
- Trajectory plots were written to `outputs/sapien/plots/`.
- Local HTML preview was written to `outputs/sapien/viewer.html`.

## 2026-05-29 Phase 2 RoboTwin DP Smoke

Working directory:

```bash
cd /home/robotics/桌面/Embodied-AI/Robotics-Introduction-Project
```

Smoke config:

```bash
configs/robotwin/demo_clean_smoke.yml
```

RoboTwin smoke data generation:

```bash
pixi run robotwin-dp-smoke-collect
```

Observed result:

- Task: `grab_roller`
- Config: `demo_clean_smoke`
- Expert seed collection: 5/5 successful.
- Output data directory: `outputs/robotwin/artifacts/data/grab_roller/demo_clean_smoke`
- Directory size: about `393M`.

DP preprocessing:

```bash
pixi run robotwin-dp-smoke-process
```

Observed zarr:

- Path: `outputs/robotwin/artifacts/dp_data/grab_roller-demo_clean_smoke-5.zarr`
- `head_camera`: `(6289, 3, 240, 320)`
- `state`: `(6289, 14)`
- `action`: `(6289, 14)`
- `episode_ends`: `[1260, 2508, 3718, 4989, 6289]`

DP debug training:

```bash
pixi run robotwin-dp-smoke-train
```

Observed result:

- Training log: `outputs/robotwin/artifacts/dp_data/outputs/grab_roller_dp_smoke_seed0/logs.json.txt`
- Checkpoints:
  - `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_smoke-5-0/1.ckpt`
  - `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_smoke-5-0/2.ckpt`
- Debug training ran for 2 epochs with 3 train/val steps per epoch.

Official eval startup check:

```bash
pixi run robotwin-dp-smoke-eval-start
```

Observed result:

- The default official eval path targets 100 test seeds, so the smoke command is timeout-protected.
- A timeout-protected run created `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_smoke/demo_clean_smoke/2026-05-29 10:40:40/episode0.mp4` before timeout.

Custom single rollout:

```bash
pixi run robotwin-dp-smoke-rollout
```

Observed result:

- Output viewer: `outputs/robotwin/single_rollouts/grab_roller/demo_clean_smoke_seed0_ckpt2_20260529-104835/viewer.html`
- Output video: `outputs/robotwin/single_rollouts/grab_roller/demo_clean_smoke_seed0_ckpt2_20260529-104835/episode0.mp4`
- Video metadata: `320x240`, `400` frames, `40.0s`.
- Smoke rollout result: `0/1`; this is not used as the final success-rate claim.

Execution policy:

- Phase 2 smoke runs are lightweight enough for agent-side background execution.
- Phase 3-5 full data generation, training, and eval runs should be packaged as one-click serial scripts and executed by the user in the foreground.

## 2026-05-29 Phase 3-5 Foreground Scripts

The three heavy stages are packaged as foreground serial scripts. The agent should not launch these commands automatically; the user runs them and reports the result afterward.

Default full-task configuration:

```bash
configs/robotwin/demo_clean_100.yml
```

The config keeps RoboTwin `demo_clean` domain settings and raises `episode_num` to 100.

Heavy artifacts are stored inside this course project by default:

```bash
outputs/robotwin/artifacts/
```

The scripts create symlinks from RoboTwin's fixed runtime paths into this artifact root, so generated data, DP zarr files, checkpoints, and eval outputs do not live in the adjacent `RoboTwin-Project` folder.

Phase 3 data generation:

```bash
pixi run robotwin-phase3-generate
```

Phase 4 DP preprocessing and training:

```bash
pixi run robotwin-phase4-train
```

Phase 5 official eval and custom rollout export:

```bash
pixi run robotwin-phase5-eval
```

Useful overrides:

```bash
TASKS="grab_roller adjust_bottle place_burger_fries" \
TASK_CONFIG=demo_clean_100 \
EXPERT_DATA_NUM=100 \
GPU_ID=0 \
pixi run robotwin-phase3-generate

TASK_CONFIG=demo_clean_100 \
EXPERT_DATA_NUM=100 \
TRAIN_EPOCHS=100 \
CHECKPOINT_EVERY=100 \
BATCH_SIZE=16 \
MAX_TRAIN_STEPS=null \
MAX_VAL_STEPS=null \
USE_EMA=True \
pixi run robotwin-phase4-train

TASK_CONFIG=demo_clean_100 \
CKPT_SETTING=demo_clean_100 \
EXPERT_DATA_NUM=100 \
CHECKPOINT_NUM=100 \
pixi run robotwin-phase5-eval
```

Expected key outputs:

- Data: `outputs/robotwin/artifacts/data/<task>/demo_clean_100/`
- Zarr: `outputs/robotwin/artifacts/dp_data/<task>-demo_clean_100-100.zarr`
- Checkpoint: `outputs/robotwin/artifacts/checkpoints/<task>-demo_clean_100-100-0/100.ckpt`
- Official eval: `outputs/robotwin/artifacts/eval_result/<task>/DP/demo_clean_100/demo_clean_100/<timestamp>/`
- Custom rollout viewer: `outputs/robotwin/single_rollouts/<task>/.../viewer.html`

## 2026-05-29 Phase 3 Data Generation Result

User foreground command completed:

```bash
pixi run robotwin-phase3-generate
```

Log directory:

```bash
outputs/robotwin/logs/phase3_20260529-111119
```

After completion, the generated data was migrated into the course project artifact root and RoboTwin runtime paths were converted to symlinks.

| Task | Data directory | HDF5 | Videos | Instructions | Seed count | Size | Seed search failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `grab_roller` | `outputs/robotwin/artifacts/data/grab_roller/demo_clean_100` | 100 | 100 | 100 | 100 | 577M | 4 / 104 tries |
| `adjust_bottle` | `outputs/robotwin/artifacts/data/adjust_bottle/demo_clean_100` | 100 | 100 | 100 | 100 | 849M | 31 / 131 tries |
| `place_burger_fries` | `outputs/robotwin/artifacts/data/place_burger_fries/demo_clean_100` | 100 | 100 | 100 | 100 | 1.9G | 3 / 103 tries |

Each task directory also contains `seed.txt` and `scene_info.json`.

## 2026-05-29 Phase 4 OOM Adjustment

The first Phase 4 foreground attempt failed on `grab_roller` during the first training batch:

```text
torch.OutOfMemoryError: CUDA out of memory
batch_size: 128
GPU capacity: 11.60 GiB
```

Root cause:

- The scripts train tasks serially, so this was not caused by training three tasks at once.
- The failure happened before completing the first `grab_roller` batch.
- The image encoder receives `batch_size x n_obs_steps` RGB observations, so `128 x 3` 240x320 images through ResNet is too aggressive for a 12GB GPU.
- Reducing the number of tasks only reduces total runtime. Reducing `EXPERT_DATA_NUM` reduces steps per epoch and disk/zarr size, but does not directly reduce per-step GPU activation memory when `BATCH_SIZE` remains too large.

Initial low-memory Phase 4 default:

```bash
BATCH_SIZE=16
MAX_TRAIN_STEPS=100
MAX_VAL_STEPS=20
USE_EMA=False
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

The failed attempt already created:

```text
outputs/robotwin/artifacts/dp_data/grab_roller-demo_clean_100-100.zarr
```

The script now skips an existing zarr by default. Set `REPROCESS_ZARR=1` to regenerate it.

If the low-memory default still OOMs, retry:

```bash
BATCH_SIZE=8 pixi run robotwin-phase4-train
```

Follow-up default adjustment:

- The user verified `BATCH_SIZE=32` reached epoch 171 on `grab_roller` without OOM.
- The observed loss was about `0.0166`, and the run was interrupted manually because 600 epochs was longer than needed for the course demonstration.
- Phase 4 now defaults to a 200-epoch course profile:

```bash
TRAIN_EPOCHS=200
CHECKPOINT_EVERY=200
BATCH_SIZE=32
MAX_TRAIN_STEPS=100
MAX_VAL_STEPS=20
USE_EMA=False
pixi run robotwin-phase4-train
```

- At this point Phase 5 was temporarily aligned to `CHECKPOINT_NUM=200`; this was later superseded by the final quality profile and `CHECKPOINT_NUM=100`.
- If `BATCH_SIZE=32` OOMs on a later run, retry `BATCH_SIZE=16 pixi run robotwin-phase4-train`; if needed, retry `BATCH_SIZE=8 pixi run robotwin-phase4-train`.

## 2026-05-29 Phase 4 Training Result

User foreground command completed:

```bash
pixi run robotwin-phase4-train
```

Log directory:

```text
outputs/robotwin/logs/phase4_20260529-144921
```

Completed checkpoints:

```text
outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_100-100-0/200.ckpt
outputs/robotwin/artifacts/checkpoints/adjust_bottle-demo_clean_100-100-0/200.ckpt
outputs/robotwin/artifacts/checkpoints/place_burger_fries-demo_clean_100-100-0/200.ckpt
```

Final structured log records:

| Task | Final train loss | Final val loss |
| --- | ---: | ---: |
| `grab_roller` | 0.00899 | 0.00857 |
| `adjust_bottle` | 0.01005 | 0.01016 |
| `place_burger_fries` | 0.01116 | 0.00976 |

Summary:

```text
outputs/robotwin/summary/phase4_training_summary.md
```

Phase 4 is complete. The next foreground command is:

```bash
pixi run robotwin-phase5-eval
```

## 2026-05-30 Phase 4 Quality Retraining Result

The final Phase 4 course profile uses the full dataloader and EMA:

```bash
TRAIN_EPOCHS=100 \
CHECKPOINT_EVERY=100 \
BATCH_SIZE=16 \
MAX_TRAIN_STEPS=null \
MAX_VAL_STEPS=null \
USE_EMA=True \
pixi run robotwin-phase4-train
```

Log directory:

```text
outputs/robotwin/logs/phase4_20260529-224707
```

Completed final checkpoints:

```text
outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_100-100-0/100.ckpt
outputs/robotwin/artifacts/checkpoints/adjust_bottle-demo_clean_100-100-0/100.ckpt
outputs/robotwin/artifacts/checkpoints/place_burger_fries-demo_clean_100-100-0/100.ckpt
```

## 2026-05-30 Phase 5 Evaluation Result

User foreground command completed:

```bash
CHECKPOINT_NUM=100 pixi run robotwin-phase5-eval
```

Log directory:

```text
outputs/robotwin/logs/phase5_20260530-092044
```

Official eval results:

| Task | Success rate | Result file |
| --- | ---: | --- |
| `grab_roller` | 100% | `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_100/demo_clean_100/2026-05-30 09:20:46/_result.txt` |
| `adjust_bottle` | 71% | `outputs/robotwin/artifacts/eval_result/adjust_bottle/DP/demo_clean_100/demo_clean_100/2026-05-30 09:49:09/_result.txt` |
| `place_burger_fries` | 98% | `outputs/robotwin/artifacts/eval_result/place_burger_fries/DP/demo_clean_100/demo_clean_100/2026-05-30 10:58:14/_result.txt` |

Custom rollout viewers:

```text
outputs/robotwin/single_rollouts/grab_roller/demo_clean_100_seed0_ckpt100_20260530-094826/viewer.html
outputs/robotwin/single_rollouts/adjust_bottle/demo_clean_100_seed0_ckpt100_20260530-105724/viewer.html
outputs/robotwin/single_rollouts/place_burger_fries/demo_clean_100_seed0_ckpt100_20260530-121045/viewer.html
```

Summary:

```text
outputs/robotwin/summary/phase5_eval_summary.md
```

Standalone single-rollout showcase, without official 100-trial eval:

```bash
pixi run robotwin-phase5-single-rollout
```

Browser-served showcase:

```bash
WEB_SERVER=1 OPEN_BROWSER=1 pixi run robotwin-phase5-single-rollout
# or:
pixi run robotwin-phase5-single-rollout-web
```

Native SAPIEN viewer showcase:

```bash
SAPIEN_VIEWER=1 RENDER_FREQ=1 pixi run robotwin-phase5-single-rollout
# or:
pixi run robotwin-phase5-single-rollout-native
```

Native mode generates a temporary task config with `render_freq` enabled under
`outputs/robotwin/artifacts/generated_configs/` and copies it to RoboTwin's
runtime `task_config/` directory for the run.

This standalone script loads the three final DP checkpoints and runs exactly one
rollout per task. It writes `index.html`, `manifest.json`, per-task
`viewer.html`, `_result.txt`, and `episode0.mp4` under:

```text
outputs/robotwin/single_rollouts/showcase_<timestamp>/
```

## 2026-05-30 Phase 6 Visual and Result Packaging

Phase 6 is a lightweight organization step. It does not rerun SAPIEN, RoboTwin
data generation, DP training, or official eval. It records the final artifact
paths for report/PPT/video use and generates a small training-loss visualization
from the existing DP logs.

Generated Phase 6 index:

```text
outputs/phase6_visual_index.md
```

Final result table:

```text
outputs/robotwin/summary/final_success_rates.md
outputs/robotwin/summary/final_success_rates.csv
```

Training-loss artifacts generated from existing `logs.json.txt` files:

```text
outputs/robotwin/summary/training_loss_curves.png
outputs/robotwin/summary/training_loss_epoch_summary.csv
```

Presentation video segment plan:

```text
outputs/video_segment_plan.md
```

Important reporting boundary:

- Official eval success rates are the quantitative results.
- Custom single-rollout videos are presentation artifacts.
- Training loss is optimization evidence, not task success.
