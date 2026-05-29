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
