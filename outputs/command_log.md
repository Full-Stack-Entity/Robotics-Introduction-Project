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
