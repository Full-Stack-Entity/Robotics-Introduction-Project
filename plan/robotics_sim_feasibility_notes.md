# Notes: Robotics Simulation Feasibility Review

## Local Sources

### Course PDF
- File: `2026机器人学导论实验——课程报告说明.pdf`
- Key requirements:
  - Simulation report accounts for 45% of the course grade.
  - Deliverables are document, PPT, and video, each 15%.
  - Required simulation functions:
    - Manipulator point control: specified motion through six spatial points.
    - Pose control: figure-eight motion and elliptical trajectory.
  - Additional controls or functions are open-ended and uncapped.
  - Report must include platform/environment, trajectory planning design, control process, simulation effect, pseudocode, result analysis, references, and formatting.
  - Video must show the student on camera and include clear explanation.
  - Deadline: 2026-06-08 24:00.

### Current Project Folder
- Folder is not a git repository.
- Local materials currently include:
  - Course requirement PDF.
  - LaTeX template project.
  - This planning folder.

### Adjacent RoboTwin Project
- Path: `../RoboTwin-Project`
- Existing evidence from local files and memory:
  - Prior ACT experiment packaging exists under `hf_release/model` and `hf_release/artifacts`.
  - Prior task used RoboTwin `beat_block_hammer`, 50 expert trajectories, ACT checkpoints, dataset statistics, result JSON, and rollout videos.
  - Existing rollout videos provide fallback material if a fresh policy rollout becomes expensive.
- Current local checks:
  - RoboTwin upstream checkout commit: `958a6d2`.
  - Checkout has existing local modifications in `collect_data.sh`, `envs/robot/planner.py`, and `policy/ACT/SIM_TASK_CONFIGS.json`; do not revert them.
  - `hf_release/artifacts` contains `200` mp4 rollout videos.
  - `beat_block_hammer/demo_clean` raw data has `50` HDF5 episodes, `50` mp4 videos, `50` instruction JSON files, and `50` trajectory pickle files.
  - `pixi run python-smoke` passed with Python `3.10.14`.
  - `pixi run core-import-smoke` passed, including `sapien`, `mplib`, `torch`, `open3d`, and `cv2`.
  - `pixi run act-import-smoke` passed.
  - `pixi run ffmpeg-video-smoke` passed.
  - Installed SAPIEN in that environment is `3.0.0b1`.

### Local Hardware and Storage
- GPU: NVIDIA GeForce RTX 4080 Laptop GPU, 12282 MiB VRAM, driver `595.58.03`.
- Current filesystem: 491G total, 154G available.
- Adjacent RoboTwin checkout size: `33G`.
- Staged model release size: `641M`; staged artifact release size: `41M`.

## External Sources

### SAPIEN Official Documentation
- URL: https://sapien-sim.github.io/docs/user_guide/getting_started/installation.html
- Key points:
  - SAPIEN is distributed through PyPI.
  - Supports Python 3.8-3.12 on Linux and Windows experimental.
  - Rendering requires NVIDIA or AMD GPU; GPU simulation requires NVIDIA GPU.
  - Offscreen rendering can be verified with `python -m sapien.example.offscreen`.

### SAPIEN Robot and Motion Planning Docs
- URLs:
  - https://sapien-sim.github.io/docs/user_guide/robotics/basic_robot.html
  - https://sapien-sim.github.io/docs/user_guide/robotics/motion_planning.html
  - https://sapien-sim.github.io/docs/user_guide/rendering/camera.html
- Key points:
  - SAPIEN can load robot models from URDF with `scene.create_urdf_loader()`.
  - Robot arms can be controlled with joint targets, passive-force compensation, or controllers.
  - SAPIEN recommends `mplib` for motion planning, collision-free trajectory planning, and IK, without requiring ROS.
  - SAPIEN camera APIs support RGB, depth, point cloud, segmentation, screenshots, and offscreen rendering.

### RoboTwin 2.0 Official Documentation
- URLs:
  - https://robotwin-platform.github.io/doc/usage/robotwin-install.html
  - https://robotwin-platform.github.io/doc/usage/collect-data.html
  - https://robotwin-platform.github.io/doc/usage/control-robot.html
  - https://robotwin-platform.github.io/doc/usage/ACT.html
- Key points:
  - RoboTwin 2.0 best supports Linux + NVIDIA GPU for CPU sim, GPU sim, and rendering.
  - Recommended stack includes Python 3.10 and CUDA 12.1.
  - Data collection uses `bash collect_data.sh ${task_name} ${task_config} ${gpu_id}`.
  - Collected episodes include HDF5 data, instructions, trajectory data, scene info, seeds, and videos.
  - Control supports `qpos` joint-position actions and `ee` end-effector pose actions.
  - ACT workflow includes preprocessing, training, and evaluation scripts; evaluation saves videos under `eval_result`.

### RoboTwin 2.0 Leaderboard
- URL: https://robotwin-platform.github.io/leaderboard
- Extraction note: `defuddle` CLI is not installed locally, so the page was read through browser/web retrieval rather than local Defuddle extraction.
- Benchmark setup used by the leaderboard:
  - Single-task training.
  - Aloha-AgileX embodiment.
  - `50` `demo_clean` demonstrations per task.
  - Evaluation uses `100` rollouts under `demo_clean` Easy and `demo_randomized` Hard.
- DP task candidates with useful Easy/demo_clean performance:
  - `grab_roller`: DP Easy `98%`, Hard `0%`.
  - `adjust_bottle`: DP Easy `97%`, Hard `0%`.
  - `place_burger_fries`: DP Easy `72%`, Hard `0%`.
  - `shake_bottle`: DP Easy `65%`, Hard `8%`.
  - `stack_bowls_three`: DP Easy `63%`, Hard `0%`.
  - `stack_bowls_two`: DP Easy `61%`, Hard `0%`.
  - `click_alarmclock`: DP Easy `61%`, Hard `5%`.
  - `shake_bottle_horizontally`: DP Easy `59%`, Hard `18%`.
- DP tasks to avoid as primary success demonstrations:
  - `lift_pot`: DP Easy `39%`, Hard `0%`.
  - `beat_block_hammer`: DP Easy `42%`, Hard `0%`.
  - Most randomized/Hard DP results are low, so randomized evaluation should be framed as a robustness stress test, not the main success criterion.
- DP3 is also in the diffusion family and has stronger leaderboard success on many tasks, but with higher engineering cost:
  - `shake_bottle_horizontally`: DP3 Easy `100%`, Hard `25%`.
  - `handover_mic`: DP3 Easy `100%`, Hard `3%`.
  - `adjust_bottle`: DP3 Easy `99%`, Hard `3%`.
  - `grab_roller`: DP3 Easy `98%`, Hard `2%`.
  - `shake_bottle`: DP3 Easy `98%`, Hard `19%`.
  - `lift_pot`: DP3 Easy `97%`, Hard `0%`.
- DP3 requires point-cloud data (`data_type.pointcloud: true`) and heavier training defaults; do not choose it unless we budget time for pointcloud data collection and batch-size tuning.

### Local DP/DP3 Script Findings
- DP has a complete chain:
  - `policy/DP/process_data.sh <task_name> <task_config> <expert_data_num>`
  - `policy/DP/train.sh <task_name> <task_config> <expert_data_num> <seed> <action_dim> <gpu_id>`
  - `policy/DP/eval.sh <task_name> <task_config> <ckpt_setting> <expert_data_num> <seed> <gpu_id>`
- DP uses head-camera RGB plus low-dimensional robot state and 14-dim or 16-dim action configs.
- DP default training config uses ResNet18 image encoder, diffusion UNet, batch size `128`, and `600` epochs.
- DP3 has a complete chain too, but it consumes point clouds and defaults to much heavier settings: batch size `256`, num_workers `8`, and `3000` epochs.
- For course feasibility, DP is the first-choice policy family; DP3 is better treated as optional if DP finishes early.
- Existing `beat_block_hammer/demo_clean` raw 50-episode dataset is `306M`, so RGB/qpos raw data is not the storage bottleneck. DP3 point-cloud data and processed zarr files will be larger.

### Task Semantics from Local Environment Scripts
- `grab_roller`: bimanual grasp and lift a roller; very clear visual success signal.
- `adjust_bottle`: single-arm grasp, lift, and place/adjust bottle; very high DP Easy success and simple success check.
- `place_burger_fries`: dual-arm pick and place burger/fries onto tray; strong visual appeal for PPT/video.
- `shake_bottle` / `shake_bottle_horizontally`: grasp and shake bottle; dynamic visual motion, useful for showing temporal action modeling.
- `stack_bowls_two`: stack two bowls; visually intuitive but lower DP margin than the top two tasks.
- `click_alarmclock`: short button-click task; good backup task if data generation/training time is tight.

### RoboTwin 2.0 arXiv
- URL: https://arxiv.org/abs/2506.18088
- Key points:
  - RoboTwin 2.0 is presented as a scalable data generator and benchmark for robust bimanual manipulation.
  - It covers 50 dual-arm tasks and five robot embodiments.
  - It emphasizes domain randomization across clutter, lighting, background, tabletop height, and language.

## Synthesized Findings

- The proposed plan is feasible if the grading-critical deliverable remains the deterministic SAPIEN-based arm simulation.
- RoboTwin2.0 is feasible as an extension/demo because the adjacent project already has a working environment and prior end-to-end evidence; final course results should still be freshly generated/trained.
- The main implementation risk is not simulator capability, but scope control: RoboTwin training/data generation can be time and disk/GPU expensive.
- Fresh RoboTwin DP training for 3-5 selected tasks is feasible if restricted to `demo_clean` and to 100-200 samples per task.
- If the priority is leaderboard success and visual polish over minimum engineering risk, DP3 may be worth a separate feasibility smoke test on one top task before committing to 3-5 tasks.
- Existing artifacts should not be presented as the final result; they are only environment validation evidence.
- The report/video should present randomized evaluation, if run, as a robustness stress test because DP leaderboard Hard performance is usually low.
- The report should frame the two layers clearly:
  - Required robotics layer: trajectory generation, IK/motion planning, control, screenshots/videos, reproducible script.
  - Extension embodied-AI layer: RoboTwin data generation, DP imitation learning, policy rollout, success/failure analysis.
