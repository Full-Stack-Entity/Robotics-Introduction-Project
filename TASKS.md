# 机器人学导论自主设计仿真任务清单

更新时间：2026-05-29

## 总目标

完成一个兼顾传统机器人学与具身智能的课程仿真项目：

1. 使用 SAPIEN 完成课程必选的机械臂点位控制与位姿/轨迹控制仿真。
2. 使用 RoboTwin2.0 重新生成数据、重新训练 Diffusion Policy 系模型，并在 3 个任务上完成评估与一次 rollout 展示。
3. 产出 LaTeX 报告 PDF、PPT、视频讲稿与可复现实验命令。

本计划已进入执行阶段。Phase 3-5 的重资源数据生成、训练和完整评测由脚本化命令串行封装，用户在前台执行。

## 当前项目状态

- [x] 当前工作目录：`/home/robotics/桌面/Embodied-AI/Robotics-Introduction-Project`
- [x] 已读取课程要求 PDF：`2026机器人学导论实验——课程报告说明.pdf`
- [x] 已完成可行性调研：
  - `plan/robotics_sim_feasibility_review.md`
  - `plan/robotics_sim_feasibility_notes.md`
  - `plan/robotics_sim_feasibility_task_plan.md`
- [x] 已确认当前课程目录不是 git 仓库；正式实现前需要初始化 git 或保留清晰快照。
- [x] 已确认相邻 RoboTwin 项目可作为环境基础：`../RoboTwin-Project/RoboTwin`
- [x] 已确认 RoboTwin 旧 ACT 结果不能作为最终课程结果；只作为环境曾经跑通的证据。

## 课程硬性要求映射

| 课程要求 | 本项目对应交付 |
| --- | --- |
| 使用的平台和实验环境配置 | 报告中分别写 SAPIEN 环境、RoboTwin/pixi 环境、GPU/依赖版本 |
| 机器人轨迹规划设计 | SAPIEN 六点点位控制、8字形轨迹、椭圆轨迹 |
| 控制过程 | SAPIEN 编程控制流程 + RoboTwin expert/data/policy/eval 流程 |
| 仿真效果 | SAPIEN 可视化/视频 + RoboTwin rollout 视频 |
| 伪代码 | 报告中给出 SAPIEN 控制伪代码与 RoboTwin DP 训练伪代码 |
| 结果分析 | 轨迹跟踪效果、RoboTwin 成功率、失败案例、Easy/Hard 泛化差异 |
| 参考文献 | SAPIEN、RoboTwin2.0、Diffusion Policy、课程材料 |
| Word/PPT/视频 | 用 LaTeX 生成 PDF，另做 PPT 与本人出镜讲解视频 |

## 验收标准

### 基础 SAPIEN 任务

- [ ] 可运行脚本完成机械臂指定空间 6 个点的点位控制。
- [ ] 可运行脚本完成末端 8 字形轨迹。
- [ ] 可运行脚本完成末端椭圆轨迹。
- [ ] 每个任务记录轨迹、关键帧和最终可视化效果。
- [ ] 优先支持在线播放或交互预览；若无法稳定实现，则自动生成 mp4 录制视频。
- [ ] 输出报告可用的图片、轨迹图、视频文件路径和环境配置。

### RoboTwin2.0 拓展任务

- [ ] 不复用旧 ACT checkpoint 作为最终结果。
- [ ] 至少完成 3 个任务的 fresh data generation。
- [ ] 至少完成 3 个任务的 fresh DP 训练或可解释的降级训练。
- [ ] 使用官方评测脚本生成每个任务的成功率、日志和评测视频。
- [ ] 额外编写一个自定义单次 rollout 展示脚本，对 3 个训练后模型各跑一次 rollout。
- [ ] 自定义 rollout 展示脚本优先支持在线播放或轻量 Web 可视化；如果不可行，则自动导出 mp4。
- [ ] 报告中明确区分官方评测结果与自定义展示 rollout：前者用于定量结果，后者用于视频/PPT展示。

### 文档与展示

- [ ] LaTeX 报告 PDF 内容完整，可复现实验操作。
- [ ] PPT 展示路线清晰：课程要求 -> SAPIEN 传统控制 -> RoboTwin 具身智能拓展 -> 结果分析。
- [ ] 视频讲稿包含对应实验内容标注，便于一边执行/播放仿真一边讲解。
- [ ] 视频中本人出镜，讲解完整清晰。

## 任务选择

### 主线策略

- 默认策略：Diffusion Policy / DP。
- 训练方式：同一 policy family，按任务分别训练 checkpoint。
- 不做 true multi-task single-checkpoint，除非后续明确升级目标。
- `demo_randomized` 作为 robustness stress test，而不是主要成功展示目标。

### 主推 3 个 DP 任务

| 优先级 | 任务 | Leaderboard DP Easy | Leaderboard DP Hard | 选择理由 |
| --- | --- | ---: | ---: | --- |
| P0 | `grab_roller` | 98% | 0% | 双臂抓取并抬起，成功信号直观，适合作为 smoke 与主展示。 |
| P0 | `adjust_bottle` | 97% | 0% | 单臂抓取/抬起/调整，成功率高，适合稳定交付。 |
| P1 | `place_burger_fries` | 72% | 0% | 汉堡和薯条放置到托盘，视觉语义强，适合 PPT/视频展示。 |

### 可选第 4/5 个任务

| 优先级 | 任务 | Leaderboard DP Easy | Leaderboard DP Hard | 使用条件 |
| --- | --- | ---: | ---: | --- |
| P2 | `stack_bowls_two` | 61% | 0% | 三任务完成后，有余力再做；展示堆叠操作。 |
| P2 | `shake_bottle_horizontally` | 59% | 18% | 动作动态效果好，Hard 相对更高；但 Easy margin 较低。 |
| P2 | `click_alarmclock` | 61% | 5% | 短任务备选，适合时间紧张时保底。 |

### 暂不作为 DP 主展示

- `lift_pot`：DP Easy 39%，风险偏高。
- `beat_block_hammer`：DP Easy 42%，已有经验但不适合作为 DP 课程主展示。
- 任何依赖 DP Hard 成功率作为主结论的任务。

## 计划目录结构

正式执行时优先创建以下目录：

```text
scripts/
  sapien/
    run_required_controls.py
    export_visualization.py
  robotwin/
    run_dp_pipeline.py
    single_rollout_demo.py
    summarize_eval_results.py
outputs/
  sapien/
    frames/
    videos/
    plots/
    logs/
  robotwin/
    configs/
    eval_results/
    single_rollouts/
    summary/
report/
  figures/
  tables/
  video_script.md
```

说明：

- 文件名是计划名，执行时可根据实际代码结构微调。
- 代码文件保持小文件原则，单文件尽量控制在 200-400 行。
- 训练大文件、视频和中间数据不提交到公开仓库；只在报告中引用相对路径与关键结果。

## 阶段计划

### Phase 0：执行前准备

- [x] 用户确认本 `TASKS.md`。
- [x] 初始化 git 或创建明确文件快照。
- [x] 创建 `scripts/`、`outputs/`、`report/` 等目录。
- [x] 记录当前 Python、GPU、CUDA、SAPIEN、RoboTwin、pixi 环境：`outputs/environment.md`。
- [x] 建立命令日志模板，确保报告可复现：`outputs/command_log.md`。

验收：

- [x] 有可追踪的项目快照：`9941614` (`phase0-baseline`)。
- [x] 有环境记录文件。
- [x] 用户确认任务范围没有偏离课程要求。

### Phase 1：SAPIEN 基础仿真任务

- [x] 选择机械臂模型与场景配置：RoboTwin Franka Panda URDF + MPlib IK + SAPIEN 第三人称渲染。
- [x] 实现六点点位控制：`six_points`。
- [x] 实现 8 字形末端轨迹：`figure_eight`。
- [x] 实现椭圆末端轨迹：`ellipse`。
- [x] 保存每个任务的轨迹数据、关键帧和最终视频：`outputs/sapien/summary.md`。
- [x] 优先尝试交互/在线播放预览：`pixi run sapien-basic-live` 启动浏览器 MJPEG 实时预览；离线中文回放页为 `outputs/sapien/viewer.html`。
- [x] 如果交互预览不稳定，则实现 mp4 导出作为兜底：`outputs/sapien/videos/*.mp4`。

验收：

- [x] 一条命令可重跑 SAPIEN 基础任务：`pixi run sapien-basic-tasks`。
- [x] 三类必选控制都有可视化产物。
- [x] 报告中可写出轨迹规划、控制过程和伪代码。

### Phase 2：RoboTwin DP smoke

- [x] 基于 `grab_roller` 创建小规模 smoke 配置：`configs/robotwin/demo_clean_smoke.yml`。
- [x] 生成 5 条 `demo_clean_smoke` 数据：`outputs/robotwin/artifacts/data/grab_roller/demo_clean_smoke`。
- [x] 跑通 DP 数据预处理：`outputs/robotwin/artifacts/dp_data/grab_roller-demo_clean_smoke-5.zarr`。
- [x] 跑通 DP 训练启动：debug training 生成 `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_smoke-5-0/2.ckpt`。
- [x] 跑通官方 eval 启动：90s timeout 前已写出 `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_smoke/demo_clean_smoke/2026-05-29 10:40:40/episode0.mp4`。
- [x] 跑通自定义单次 rollout 展示脚本的最小版本：`pixi run robotwin-dp-smoke-rollout`。

验收：

- [x] `grab_roller` smoke 数据、训练日志、eval 产物存在：`outputs/robotwin/summary/phase2_dp_smoke_summary.md`。
- [x] 自定义 rollout 脚本可以调用训练后模型并输出可视化结果：`outputs/robotwin/single_rollouts/grab_roller/demo_clean_smoke_seed0_ckpt2_20260529-104835/viewer.html`。
- [x] 明确继续 DP 主线；暂不切换 DP3。Phase 3-5 的重资源命令由 agent 撰写一键串行脚本，用户在前台执行。

### Phase 3：RoboTwin 三任务数据生成

- [x] 生成 Phase 3 串行前台执行脚本：`scripts/robotwin/phase3_generate_data.sh`。
- [x] 为 `grab_roller` 生成 100 条 `demo_clean_100` clean-domain 数据：`outputs/robotwin/artifacts/data/grab_roller/demo_clean_100`。
- [x] 为 `adjust_bottle` 生成 100 条 `demo_clean_100` clean-domain 数据：`outputs/robotwin/artifacts/data/adjust_bottle/demo_clean_100`。
- [x] 为 `place_burger_fries` 生成 100 条 `demo_clean_100` clean-domain 数据：`outputs/robotwin/artifacts/data/place_burger_fries/demo_clean_100`。
- [x] 统计每个任务的数据量、视频、HDF5、instruction、seed、scene_info：`outputs/robotwin/summary/phase3_data_summary.md`。
- [x] 记录 seed search 失败次数；三个任务均成功生成 100 条，不需要调整任务或样本数。

验收：

- [x] 一条前台命令封装三任务串行数据生成：`pixi run robotwin-phase3-generate`。
- [x] 三个任务各有完整数据目录。
- [x] 每个任务都有至少一个 expert demonstration 视频可用于说明数据生成流程。
- [x] 数据目录结构和命令写入 `outputs/command_log.md` 与 Phase3 summary。

### Phase 4：RoboTwin DP 训练

- [x] 生成 Phase 4 串行前台执行脚本：`scripts/robotwin/phase4_train_dp.sh`。
- [ ] 对 `grab_roller` 进行 DP 预处理与训练。
- [ ] 对 `adjust_bottle` 进行 DP 预处理与训练。
- [ ] 对 `place_burger_fries` 进行 DP 预处理与训练。
- [ ] 记录训练命令、训练时长、显存占用、loss 曲线和 checkpoint 路径。
- [ ] 如果默认 batch size/epochs 不适合本机，进行保守调参并记录原因。

验收：

- [x] 一条前台命令封装三任务 DP 预处理与训练：`pixi run robotwin-phase4-train`。
- [ ] 三个任务都有训练日志和 checkpoint。
- [ ] 每个任务至少保存一个可用于 eval 的 checkpoint。
- [ ] 报告可复现命令完整。

### Phase 5：官方评测与自定义单次 rollout

- [x] 生成 Phase 5 串行前台执行脚本：`scripts/robotwin/phase5_eval_rollout.sh`。
- [ ] 使用官方 DP eval 脚本评估 `grab_roller`。
- [ ] 使用官方 DP eval 脚本评估 `adjust_bottle`。
- [ ] 使用官方 DP eval 脚本评估 `place_burger_fries`。
- [ ] 汇总成功率、rollout 数量、失败案例和视频路径。
- [ ] 编写 `single_rollout_demo.py`，对三个任务各执行一次训练后模型 rollout。
- [ ] 单次 rollout 脚本优先提供在线播放/交互预览入口。
- [ ] 如果在线播放不可行，则自动保存每个任务的 mp4。

验收：

- [x] 一条前台命令封装三任务官方评测与展示 rollout：`pixi run robotwin-phase5-eval`。
- [ ] 官方评测结果存在并可被报告引用。
- [ ] 自定义单次 rollout 展示脚本可重跑。
- [ ] 三个任务各有一个展示级视频或在线播放入口。
- [ ] 官方评测与自定义展示在报告中明确区分。

### Phase 6：可视化与结果整理

- [ ] 整理 SAPIEN 必选任务视频与关键帧。
- [ ] 整理 RoboTwin expert demonstration、official eval、single rollout 三类视频。
- [ ] 生成训练曲线、成功率表、任务对比表。
- [ ] 选择视频中要播放的片段。
- [ ] 标注每个视频片段对应的讲解点。

验收：

- [ ] `outputs/` 下有清晰的视频、图片、表格目录。
- [ ] PPT 和报告可以直接引用这些产物。
- [ ] 视频讲稿知道每一段展示什么、讲什么。

### Phase 7：LaTeX 报告

- [ ] 基于现有 LaTeX 模板建立正式报告。
- [ ] 写实验背景与平台选择。
- [ ] 写 SAPIEN 机械臂轨迹规划与控制实现。
- [ ] 写 RoboTwin 数据生成、DP 模型训练与评测流程。
- [ ] 写结果分析和失败案例。
- [ ] 写参考文献。
- [ ] 编译 PDF 并修复格式问题。

验收：

- [ ] PDF 可正常编译。
- [ ] 报告满足课程 PDF 中列出的内容完整性要求。
- [ ] 所有图表和视频引用路径可追踪。

### Phase 8：PPT 与视频讲稿

- [ ] 制作 PPT 大纲。
- [ ] 加入 SAPIEN 基础任务图/视频。
- [ ] 加入 RoboTwin 三任务训练与 rollout 结果。
- [ ] 撰写口语化视频讲稿。
- [ ] 在讲稿中标注对应实验内容、播放视频和执行命令的位置。
- [ ] 给出最终录制流程。

验收：

- [ ] PPT 可用于 5-10 分钟展示。
- [ ] 讲稿能支持边播放/执行仿真边讲解。
- [ ] 视频中本人出镜要求被明确纳入录制流程。

## 关键命令草案

正式命令在实现后更新。当前先记录预期形态：

```bash
# SAPIEN required controls
python scripts/sapien/run_required_controls.py --task all --visualize --record

# RoboTwin data collection
cd ../RoboTwin-Project/RoboTwin
bash collect_data.sh grab_roller demo_clean 0
bash collect_data.sh adjust_bottle demo_clean 0
bash collect_data.sh place_burger_fries demo_clean 0

# RoboTwin DP training
cd ../RoboTwin-Project/RoboTwin/policy/DP
bash train.sh grab_roller demo_clean 100 0 14 0
bash train.sh adjust_bottle demo_clean 100 0 14 0
bash train.sh place_burger_fries demo_clean 100 0 14 0

# Official evaluation
bash eval.sh grab_roller demo_clean demo_clean 100 0 0
bash eval.sh adjust_bottle demo_clean demo_clean 100 0 0
bash eval.sh place_burger_fries demo_clean demo_clean 100 0 0

# Custom single-rollout visualization
python scripts/robotwin/single_rollout_demo.py --tasks grab_roller adjust_bottle place_burger_fries --mode web
python scripts/robotwin/single_rollout_demo.py --tasks grab_roller adjust_bottle place_burger_fries --mode record
```

注意：

- 上述命令是任务书草案，正式执行前需要核对实际脚本路径、参数和 checkpoint 命名。
- 若 `--mode web` 不稳定，使用 `--mode record` 生成 mp4。
- 官方评测脚本用于定量指标；自定义单次 rollout 用于展示。

## 风险与降级策略

| 风险 | 影响 | 降级策略 |
| --- | --- | --- |
| SAPIEN 在线可视化不稳定 | 无法实时展示 | 自动导出 mp4，并保留关键帧 |
| RoboTwin 在线 rollout 不稳定 | 展示体验受影响 | 自定义脚本直接保存 mp4 |
| DP 训练耗时过长 | 三任务无法全部完成 | 先保证 `grab_roller` 和 `adjust_bottle`，第三任务减少 epoch 或样本 |
| DP 成功率低于预期 | 展示效果受影响 | 保留 official eval 定量结果，选择最佳 checkpoint 的 single rollout 展示 |
| `demo_randomized` 成功率低 | 泛化结论不强 | 明确写为 robustness stress test，不作为主成功指标 |
| 磁盘空间不足 | 数据/视频无法完整保存 | 每任务先 100 demos；清理中间缓存；必要时迁移到租赁平台 |
| DP3 想做但资源不足 | 拔高分支失败 | 不影响 DP 主线；DP3 只在一任务 smoke 后决定 |

## 暂停点与用户确认

当前暂停在计划确认点。

请用户确认：

1. 是否批准按本 `TASKS.md` 开始执行。
2. 是否默认只做 DP 三任务主线，DP3 作为可选 smoke。
3. 是否接受“在线播放优先，mp4 录制兜底”的可视化验收方式。
