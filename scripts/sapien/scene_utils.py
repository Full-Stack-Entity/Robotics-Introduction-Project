#!/usr/bin/env python3
"""Shared SAPIEN scene helpers for the Phase 1 demo."""

from __future__ import annotations

import numpy as np
import sapien.core as sapien


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm < 1e-9:
        raise ValueError("Cannot normalize near-zero vector")
    return vector / norm


def quat_from_matrix(matrix: np.ndarray) -> np.ndarray:
    """Convert a 3x3 rotation matrix to a wxyz quaternion."""

    trace = float(np.trace(matrix))
    if trace > 0.0:
        scale = (trace + 1.0) ** 0.5 * 2.0
        return np.array(
            [
                0.25 * scale,
                (matrix[2, 1] - matrix[1, 2]) / scale,
                (matrix[0, 2] - matrix[2, 0]) / scale,
                (matrix[1, 0] - matrix[0, 1]) / scale,
            ],
            dtype=np.float64,
        )
    axis = int(np.argmax(np.diag(matrix)))
    quat = np.zeros(4, dtype=np.float64)
    if axis == 0:
        scale = (1.0 + matrix[0, 0] - matrix[1, 1] - matrix[2, 2]) ** 0.5 * 2.0
        quat[:] = [
            (matrix[2, 1] - matrix[1, 2]) / scale,
            0.25 * scale,
            (matrix[0, 1] + matrix[1, 0]) / scale,
            (matrix[0, 2] + matrix[2, 0]) / scale,
        ]
    elif axis == 1:
        scale = (1.0 + matrix[1, 1] - matrix[0, 0] - matrix[2, 2]) ** 0.5 * 2.0
        quat[:] = [
            (matrix[0, 2] - matrix[2, 0]) / scale,
            (matrix[0, 1] + matrix[1, 0]) / scale,
            0.25 * scale,
            (matrix[1, 2] + matrix[2, 1]) / scale,
        ]
    else:
        scale = (1.0 + matrix[2, 2] - matrix[0, 0] - matrix[1, 1]) ** 0.5 * 2.0
        quat[:] = [
            (matrix[1, 0] - matrix[0, 1]) / scale,
            (matrix[0, 2] + matrix[2, 0]) / scale,
            (matrix[1, 2] + matrix[2, 1]) / scale,
            0.25 * scale,
        ]
    return quat / np.linalg.norm(quat)


def look_at_pose(eye: np.ndarray, target: np.ndarray) -> sapien.Pose:
    """Create a SAPIEN camera pose using x-forward, y-left, z-up axes."""

    forward = normalize(target - eye)
    left = normalize(np.cross(np.array([0.0, 0.0, 1.0]), forward))
    up = normalize(np.cross(forward, left))
    rotation = np.column_stack([forward, left, up])
    return sapien.Pose(eye, quat_from_matrix(rotation))


def add_box(
    scene: sapien.Scene,
    name: str,
    pose: sapien.Pose,
    half_size: tuple[float, float, float],
    color: tuple[float, float, float, float],
) -> sapien.Actor:
    builder = scene.create_actor_builder()
    builder.add_box_visual(half_size=half_size, material=color)
    actor = builder.build_static(name=name)
    actor.set_pose(pose)
    return actor


def add_sphere(
    scene: sapien.Scene,
    name: str,
    radius: float,
    color: tuple[float, float, float, float],
    pose: sapien.Pose | None = None,
    kinematic: bool = True,
) -> sapien.Actor:
    builder = scene.create_actor_builder()
    builder.add_sphere_visual(radius=radius, material=color)
    actor = builder.build_kinematic(name=name) if kinematic else builder.build_static(name=name)
    if pose is not None:
        actor.set_pose(pose)
    return actor
