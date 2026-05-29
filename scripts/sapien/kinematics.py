#!/usr/bin/env python3
"""Trajectory generation and Franka Panda IK for the Phase 1 demo."""

from __future__ import annotations

import os
from dataclasses import dataclass
from math import pi
from pathlib import Path
from typing import Iterable

import mplib
import numpy as np


@dataclass(frozen=True)
class TaskSpec:
    """Named Cartesian trajectory specification."""

    name: str
    title_zh: str
    title_en: str
    targets: np.ndarray
    key_indices: tuple[int, ...]


@dataclass(frozen=True)
class FrankaConfig:
    """Paths and defaults for the RoboTwin Franka Panda asset."""

    asset_dir: Path
    urdf_path: Path
    srdf_path: Path
    move_group: str = "panda_hand"
    ee_link: str = "panda_hand"
    ee_orientation_wxyz: tuple[float, float, float, float] = (0.0, 1.0, 0.0, 0.0)
    gripper_qpos: tuple[float, float] = (0.035, 0.035)
    home_qpos: tuple[float, ...] = (
        0.0,
        0.19634954084936207,
        0.0,
        -2.617993877991494,
        0.0,
        2.941592653589793,
        0.7853981633974483,
        0.035,
        0.035,
    )


@dataclass(frozen=True)
class RobotState:
    """One solved robot state along a Cartesian task trajectory."""

    index: int
    time_s: float
    target: np.ndarray
    qpos: np.ndarray
    ee_position: np.ndarray
    error: float


def find_robotwin_root() -> Path:
    """Return the adjacent RoboTwin checkout used by the project."""

    env_root = os.environ.get("ROBOTWIN_ROOT")
    candidates = [
        Path(env_root) if env_root else None,
        Path("../RoboTwin-Project/RoboTwin"),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        root = candidate.expanduser().resolve()
        if (root / "assets" / "embodiments" / "franka-panda" / "panda.urdf").exists():
            return root
    raise FileNotFoundError("Cannot find RoboTwin Franka Panda asset directory")


def default_franka_config(robotwin_root: Path | None = None) -> FrankaConfig:
    """Build the default Franka Panda config from RoboTwin assets."""

    root = (robotwin_root or find_robotwin_root()).resolve()
    asset_dir = root / "assets" / "embodiments" / "franka-panda"
    return FrankaConfig(
        asset_dir=asset_dir,
        urdf_path=asset_dir / "panda.urdf",
        srdf_path=asset_dir / "panda.srdf",
    )


def smoothstep(value: float) -> float:
    """Cubic interpolation with zero velocity at segment boundaries."""

    return value * value * (3.0 - 2.0 * value)


def interpolate_points(points: np.ndarray, steps_per_segment: int) -> tuple[np.ndarray, tuple[int, ...]]:
    """Interpolate Cartesian waypoints with smooth segment timing."""

    if len(points) < 2:
        raise ValueError("At least two points are required")
    if steps_per_segment < 2:
        raise ValueError("steps_per_segment must be >= 2")

    samples: list[np.ndarray] = []
    key_indices = [0]
    for start, end in zip(points[:-1], points[1:]):
        segment_start = np.asarray(start, dtype=np.float64)
        segment_end = np.asarray(end, dtype=np.float64)
        for step in range(steps_per_segment):
            if samples and step == 0:
                continue
            alpha = smoothstep(step / (steps_per_segment - 1))
            samples.append((1.0 - alpha) * segment_start + alpha * segment_end)
        key_indices.append(len(samples) - 1)

    return np.asarray(samples, dtype=np.float64), tuple(key_indices)


def make_six_point_task(steps_per_segment: int) -> TaskSpec:
    """Create the required six-point spatial positioning task."""

    waypoints = np.asarray(
        [
            [0.44, -0.24, 0.34],
            [0.64, -0.20, 0.54],
            [0.68, 0.00, 0.44],
            [0.58, 0.24, 0.62],
            [0.42, 0.18, 0.50],
            [0.50, 0.00, 0.72],
        ],
        dtype=np.float64,
    )
    targets, key_indices = interpolate_points(waypoints, steps_per_segment)
    return TaskSpec("six_points", "六点空间点位控制", "Six spatial point control", targets, key_indices)


def make_figure_eight_task(num_steps: int) -> TaskSpec:
    """Create a horizontal figure-eight end-effector trajectory."""

    if num_steps < 20:
        raise ValueError("num_steps must be >= 20")
    ts = np.linspace(0.0, 2.0 * pi, num_steps, endpoint=True)
    targets = np.column_stack(
        [
            0.56 + 0.16 * np.sin(ts),
            0.24 * np.sin(ts) * np.cos(ts),
            0.54 + 0.07 * np.cos(ts),
        ]
    )
    key_indices = tuple(int(round(i * (num_steps - 1) / 7)) for i in range(8))
    return TaskSpec("figure_eight", "8 字形末端轨迹", "Figure-eight trajectory", targets, key_indices)


def make_ellipse_task(num_steps: int) -> TaskSpec:
    """Create an ellipse that stays inside the Panda IK workspace."""

    if num_steps < 20:
        raise ValueError("num_steps must be >= 20")
    ts = np.linspace(0.0, 2.0 * pi, num_steps, endpoint=True)
    targets = np.column_stack(
        [
            0.54 + 0.14 * np.cos(ts),
            0.22 * np.sin(ts),
            0.50 + 0.05 * np.sin(ts + pi / 5.0),
        ]
    )
    key_indices = tuple(int(round(i * (num_steps - 1) / 7)) for i in range(8))
    return TaskSpec("ellipse", "椭圆末端轨迹", "Elliptical trajectory", targets, key_indices)


def build_task_specs(task_names: Iterable[str], steps_per_segment: int, curve_steps: int) -> list[TaskSpec]:
    """Build task specs in caller-requested order."""

    builders = {
        "six_points": lambda: make_six_point_task(steps_per_segment),
        "figure_eight": lambda: make_figure_eight_task(curve_steps),
        "ellipse": lambda: make_ellipse_task(curve_steps),
    }
    specs: list[TaskSpec] = []
    for name in task_names:
        if name not in builders:
            valid = ", ".join(sorted(builders))
            raise ValueError(f"Unknown task {name!r}; valid tasks: {valid}")
        specs.append(builders[name]())
    return specs


class FrankaIKSolver:
    """Sequential MPlib IK solver for the RoboTwin Franka Panda."""

    def __init__(self, cfg: FrankaConfig) -> None:
        self.cfg = cfg
        self.planner = mplib.Planner(
            urdf=cfg.urdf_path,
            srdf=cfg.srdf_path,
            move_group=cfg.move_group,
            use_convex=False,
        )

    def solve_task(self, spec: TaskSpec, fps: int) -> list[RobotState]:
        qpos = np.asarray(self.cfg.home_qpos, dtype=np.float64)
        states: list[RobotState] = []
        for index, target in enumerate(spec.targets):
            qpos = self._solve_target(target=target, seed_qpos=qpos)
            states.append(
                RobotState(
                    index=index,
                    time_s=index / fps,
                    target=target,
                    qpos=qpos,
                    ee_position=target.copy(),
                    error=0.0,
                )
            )
        return states

    def _solve_target(self, target: np.ndarray, seed_qpos: np.ndarray) -> np.ndarray:
        pose = mplib.Pose(p=target.tolist(), q=list(self.cfg.ee_orientation_wxyz))
        status, qpos = self.planner.IK(
            pose,
            seed_qpos,
            n_init_qpos=50,
            threshold=0.02,
            return_closest=True,
        )
        if status != "Success" or qpos is None:
            raise RuntimeError(f"Franka IK failed for target {target.tolist()}: {status}")
        solved = np.asarray(qpos, dtype=np.float64)
        solved[-2:] = np.asarray(self.cfg.gripper_qpos, dtype=np.float64)
        return solved
