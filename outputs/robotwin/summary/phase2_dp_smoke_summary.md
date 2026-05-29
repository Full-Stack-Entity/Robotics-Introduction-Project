# Phase 2 RoboTwin DP Smoke Summary

更新时间：2026-05-29

## 目标

Phase 2 的目标是用 `grab_roller` 跑通 RoboTwin2.0 + Diffusion Policy 的最小闭环：

1. 生成小规模 `demo_clean_smoke` expert 数据。
2. 将 RoboTwin HDF5 数据转成 DP zarr 数据。
3. 启动 DP debug training 并产出 checkpoint。
4. 启动官方 eval 入口，确认 checkpoint 和环境链路可用。
5. 通过课程仓库自定义脚本跑一次 single rollout，并生成展示用 HTML viewer/mp4。

## 已验证产物

| 项目 | 路径 | 结果 |
| --- | --- | --- |
| smoke 配置副本 | `configs/robotwin/demo_clean_smoke.yml` | 5 episodes, clean background, D435 head/wrist cameras |
| expert 数据 | `outputs/robotwin/artifacts/data/grab_roller/demo_clean_smoke` | 5 个 HDF5、5 个 expert videos、instructions、seed.txt |
| DP zarr | `outputs/robotwin/artifacts/dp_data/grab_roller-demo_clean_smoke-5.zarr` | `head_camera/state/action = 6289` steps |
| DP checkpoint | `outputs/robotwin/artifacts/checkpoints/grab_roller-demo_clean_smoke-5-0/2.ckpt` | debug training checkpoint，约 1.1GB |
| DP training log | `outputs/robotwin/artifacts/dp_data/outputs/grab_roller_dp_smoke_seed0/logs.json.txt` | 2 个 debug epoch，train/val loss 正常记录 |
| 官方 eval 启动 | `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_smoke/demo_clean_smoke/2026-05-29 10:40:40/episode0.mp4` | 90s timeout 前已启动并写出视频 |
| 自定义 rollout | `outputs/robotwin/single_rollouts/grab_roller/demo_clean_smoke_seed0_ckpt2_20260529-104835/viewer.html` | 生成中文 HTML viewer 和 40s mp4 |

## 关键观测

- `grab_roller` 的 smoke seed search 为 5/5 成功，未出现 expert planning failure。
- 5 条数据约 393MB，DP zarr 约 591MB，两个 DP checkpoint 合计约 2.2GB。
- 自定义 single rollout 使用 5 条 demo + 2 个 debug epoch 的 checkpoint，结果为 `0/1`。这是 smoke 训练的预期风险，不作为最终成功率结论。
- 官方 eval 入口默认按 100 个 test seeds 运行，不适合在 Phase2 直接完整跑完；本阶段只验证其能启动并写出评测视频。

## 复现实验命令

从课程仓库根目录执行：

```bash
pixi run robotwin-dp-smoke-collect
pixi run robotwin-dp-smoke-process
pixi run robotwin-dp-smoke-train
pixi run robotwin-dp-smoke-eval-start
pixi run robotwin-dp-smoke-rollout
```

说明：

- Phase2 这些 smoke 命令较轻量，agent 可以后台执行。
- Phase3-5 的完整数据生成、训练和评测会改为一键串行脚本，由用户在前台执行。
- RoboTwin 的固定运行路径通过 symlink 指向 `outputs/robotwin/artifacts/`，数据、zarr、checkpoint 和 eval 输出默认保存在当前课程项目内。
- 定量结果以后以官方 eval 的完整 `_result.txt` 为准；`single_rollout_demo.py` 只服务于课程展示视频/PPT。
