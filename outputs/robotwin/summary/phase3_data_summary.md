# Phase 3 RoboTwin Data Generation Summary

更新时间：2026-05-29

## 目标

Phase 3 的目标是为三个 RoboTwin 拓展任务生成 fresh expert demonstrations，并把数据保存在当前课程项目目录下，避免课程产物散落在相邻 `RoboTwin-Project` 仓库中。

## 执行命令

用户在前台执行：

```bash
pixi run robotwin-phase3-generate
```

日志目录：

```text
outputs/robotwin/logs/phase3_20260529-111119
```

## Artifact 存储策略

重资源产物统一保存在：

```text
outputs/robotwin/artifacts/
```

RoboTwin 上游脚本仍然需要访问固定路径，例如 `data/<task>/<config>`、`policy/DP/data`、`policy/DP/checkpoints` 和 `eval_result/<task>`。本项目通过 `scripts/robotwin/prepare_artifact_links.py` 将这些固定路径迁移/链接到当前项目目录，从而保留上游兼容性，同时避免数据和模型实际存放在相邻项目中。

## 数据生成结果

| 任务 | 数据目录 | HDF5 | Expert video | Instruction JSON | Seed count | 目录大小 | Seed search 失败 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `grab_roller` | `outputs/robotwin/artifacts/data/grab_roller/demo_clean_100` | 100 | 100 | 100 | 100 | 577M | 4 / 104 tries |
| `adjust_bottle` | `outputs/robotwin/artifacts/data/adjust_bottle/demo_clean_100` | 100 | 100 | 100 | 100 | 849M | 31 / 131 tries |
| `place_burger_fries` | `outputs/robotwin/artifacts/data/place_burger_fries/demo_clean_100` | 100 | 100 | 100 | 100 | 1.9G | 3 / 103 tries |

每个任务目录都包含：

- `data/episode*.hdf5`
- `video/episode*.mp4`
- `instructions/episode*.json`
- `seed.txt`
- `scene_info.json`
- `_traj_data/`

## 后续使用

Phase 4 不需要重新生成数据。直接在前台执行：

```bash
pixi run robotwin-phase4-train
```

默认读取：

```text
outputs/robotwin/artifacts/data/<task>/demo_clean_100/
```

默认写入：

```text
outputs/robotwin/artifacts/dp_data/
outputs/robotwin/artifacts/checkpoints/
```
