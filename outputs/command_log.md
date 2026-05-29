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
- Output data directory: `../RoboTwin-Project/RoboTwin/data/grab_roller/demo_clean_smoke`
- Directory size: about `393M`.

DP preprocessing:

```bash
pixi run robotwin-dp-smoke-process
```

Observed zarr:

- Path: `../RoboTwin-Project/RoboTwin/policy/DP/data/grab_roller-demo_clean_smoke-5.zarr`
- `head_camera`: `(6289, 3, 240, 320)`
- `state`: `(6289, 14)`
- `action`: `(6289, 14)`
- `episode_ends`: `[1260, 2508, 3718, 4989, 6289]`

DP debug training:

```bash
pixi run robotwin-dp-smoke-train
```

Observed result:

- Training log: `../RoboTwin-Project/RoboTwin/policy/DP/data/outputs/grab_roller_dp_smoke_seed0/logs.json.txt`
- Checkpoints:
  - `../RoboTwin-Project/RoboTwin/policy/DP/checkpoints/grab_roller-demo_clean_smoke-5-0/1.ckpt`
  - `../RoboTwin-Project/RoboTwin/policy/DP/checkpoints/grab_roller-demo_clean_smoke-5-0/2.ckpt`
- Debug training ran for 2 epochs with 3 train/val steps per epoch.

Official eval startup check:

```bash
pixi run robotwin-dp-smoke-eval-start
```

Observed result:

- The default official eval path targets 100 test seeds, so the smoke command is timeout-protected.
- A timeout-protected run created `../RoboTwin-Project/RoboTwin/eval_result/grab_roller/DP/demo_clean_smoke/demo_clean_smoke/2026-05-29 10:40:40/episode0.mp4` before timeout.

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
TRAIN_EPOCHS=600 \
CHECKPOINT_EVERY=300 \
BATCH_SIZE=128 \
pixi run robotwin-phase4-train

TASK_CONFIG=demo_clean_100 \
CKPT_SETTING=demo_clean_100 \
EXPERT_DATA_NUM=100 \
CHECKPOINT_NUM=600 \
pixi run robotwin-phase5-eval
```

Expected key outputs:

- Data: `../RoboTwin-Project/RoboTwin/data/<task>/demo_clean_100/`
- Zarr: `../RoboTwin-Project/RoboTwin/policy/DP/data/<task>-demo_clean_100-100.zarr`
- Checkpoint: `../RoboTwin-Project/RoboTwin/policy/DP/checkpoints/<task>-demo_clean_100-100-0/600.ckpt`
- Official eval: `../RoboTwin-Project/RoboTwin/eval_result/<task>/DP/demo_clean_100/demo_clean_100/<timestamp>/`
- Custom rollout viewer: `outputs/robotwin/single_rollouts/<task>/.../viewer.html`
