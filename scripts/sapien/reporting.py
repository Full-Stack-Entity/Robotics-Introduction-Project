#!/usr/bin/env python3
"""Artifact writers for the Phase 1 SAPIEN demo."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np

from kinematics import RobotState, TaskSpec


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

plt.rcParams["font.sans-serif"] = [
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "Droid Sans Fallback",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


@dataclass(frozen=True)
class OutputLayout:
    """Output paths for generated SAPIEN artifacts."""

    root: Path
    frames: Path
    videos: Path
    plots: Path
    logs: Path

    @classmethod
    def from_root(cls, root: Path) -> "OutputLayout":
        return cls(root=root, frames=root / "frames", videos=root / "videos", plots=root / "plots", logs=root / "logs")

    def ensure(self) -> None:
        for path in (self.frames, self.videos, self.plots, self.logs):
            path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, states: list[RobotState]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joint_names = [f"panda_joint{i}" for i in range(1, 8)] + ["panda_finger_joint1", "panda_finger_joint2"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "index",
                "time_s",
                "target_x",
                "target_y",
                "target_z",
                "ee_x",
                "ee_y",
                "ee_z",
                *joint_names,
                "position_error_m",
            ]
        )
        for state in states:
            writer.writerow(
                [
                    state.index,
                    f"{state.time_s:.6f}",
                    *[f"{value:.6f}" for value in state.target],
                    *[f"{value:.6f}" for value in state.ee_position],
                    *[f"{value:.6f}" for value in state.qpos],
                    f"{state.error:.8f}",
                ]
            )


def write_plot(path: Path, spec: TaskSpec, states: list[RobotState]) -> None:
    targets = np.asarray([state.target for state in states])
    ee_positions = np.asarray([state.ee_position for state in states])
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(targets[:, 0], targets[:, 1], targets[:, 2], label="目标轨迹", linewidth=2.0)
    ax.plot(ee_positions[:, 0], ee_positions[:, 1], ee_positions[:, 2], "--", label="Panda 末端")
    key_points = spec.targets[list(spec.key_indices)]
    ax.scatter(key_points[:, 0], key_points[:, 1], key_points[:, 2], c="tab:green", s=28, label="关键点")
    ax.set_title(spec.title_zh)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_zlabel("z / m")
    ax.legend(loc="best")
    ax.view_init(elev=26, azim=-56)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_viewer(path: Path, artifacts: list[dict[str, str]]) -> None:
    rows = []
    for item in artifacts:
        rel_video = Path(item["video"]).relative_to(path.parent)
        rel_plot = Path(item["plot"]).relative_to(path.parent)
        rows.append(
            f"""
      <section>
        <h2>{item['title_zh']}</h2>
        <video src="{rel_video.as_posix()}" controls muted loop></video>
        <p><a href="{rel_plot.as_posix()}">查看轨迹图</a> · 最大末端误差 {item['max_error_m']} m</p>
      </section>"""
        )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAPIEN 基础任务回放</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; background: #f7f8fa; color: #1c2430; }}
    main {{ max-width: 980px; margin: 0 auto; }}
    section {{ margin: 0 0 28px; padding-bottom: 20px; border-bottom: 1px solid #d8dde6; }}
    video {{ width: 100%; max-height: 560px; background: #111; border-radius: 6px; }}
    h1, h2 {{ margin-bottom: 10px; }}
    p {{ color: #4d5968; }}
  </style>
</head>
<body>
  <main>
    <h1>SAPIEN 基础任务回放：Franka Panda 机械臂</h1>
    <p>本页播放已生成的视频；实时预览请运行 <code>pixi run sapien-basic-live</code>。</p>
    {''.join(rows)}
  </main>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def write_summary(path: Path, artifacts: list[dict[str, str]]) -> None:
    lines = [
        "# SAPIEN Phase 1 基础任务产物",
        "",
        "控制链路：`Cartesian target -> MPlib IK -> Franka Panda qpos -> SAPIEN URDF rendering`。",
        "",
        "| 任务 | 帧数 | 最大末端误差 (m) | 视频 | 轨迹图 | CSV |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for item in artifacts:
        lines.append(
            f"| {item['title_zh']} | {item['frames']} | {item['max_error_m']} | "
            f"`{item['video']}` | `{item['plot']}` | `{item['csv']}` |"
        )
    lines.extend(
        [
            "",
            "本地浏览器回放：",
            "",
            "```bash",
            "xdg-open outputs/sapien/viewer.html",
            "```",
            "",
            "实时浏览器预览：",
            "",
            "```bash",
            "pixi run sapien-basic-live",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
