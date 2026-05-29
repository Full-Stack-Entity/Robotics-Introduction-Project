#!/usr/bin/env python3
"""SAPIEN scene that renders the RoboTwin Franka Panda asset."""

from __future__ import annotations

import numpy as np
import sapien.core as sapien

from kinematics import FrankaConfig, RobotState, TaskSpec
from scene_utils import add_box, add_sphere, look_at_pose


class FrankaSapienScene:
    """Third-person SAPIEN renderer for a real Franka Panda URDF."""

    def __init__(
        self,
        cfg: FrankaConfig,
        width: int,
        height: int,
        sapien_viewer: bool = False,
    ) -> None:
        self.cfg = cfg
        self.engine = sapien.Engine()
        self.renderer = sapien.SapienRenderer()
        self.engine.set_renderer(self.renderer)
        self.scene = self.engine.create_scene(sapien.SceneConfig())
        self.scene.set_timestep(1.0 / 60.0)
        self.scene.set_ambient_light([0.48, 0.48, 0.48])
        self.scene.add_directional_light([0.4, -0.6, -1.0], [0.95, 0.95, 0.9], shadow=True)
        self.scene.add_point_light([1.2, -1.0, 1.6], [0.8, 0.76, 0.68])
        self.scene.add_ground(-0.04)
        self._add_workcell()

        loader = self.scene.create_urdf_loader()
        loader.fix_root_link = True
        self.robot = loader.load(str(cfg.urdf_path))
        self.robot.set_name("franka_panda")
        self.ee_link = self._find_link(cfg.ee_link)
        self.current_target = add_sphere(
            self.scene,
            "current_target",
            0.018,
            (0.95, 0.15, 0.15, 1.0),
            sapien.Pose([0, 0, 0], [1, 0, 0, 0]),
        )
        self.camera = self.scene.add_camera("main_camera", width, height, 0.82, 0.01, 10.0)
        self.camera.set_entity_pose(look_at_pose(np.array([1.45, -1.40, 1.05]), np.array([0.48, 0.0, 0.46])))
        self.viewer = self._create_viewer() if sapien_viewer else None

    def add_task_guides(self, spec: TaskSpec) -> None:
        for idx, target in enumerate(spec.targets[:: max(1, len(spec.targets) // 56)]):
            add_sphere(
                self.scene,
                f"path_{spec.name}_{idx}",
                0.010,
                (0.08, 0.42, 0.88, 0.45),
                sapien.Pose(target, [1, 0, 0, 0]),
            )
        for point_idx, sample_idx in enumerate(spec.key_indices):
            add_sphere(
                self.scene,
                f"target_{point_idx}",
                0.024,
                (0.05, 0.72, 0.34, 1.0),
                sapien.Pose(spec.targets[sample_idx], [1, 0, 0, 0]),
            )

    def set_state(self, state: RobotState) -> tuple[np.ndarray, float]:
        self.robot.set_qpos(state.qpos)
        self.current_target.set_pose(sapien.Pose(state.target, [1, 0, 0, 0]))
        self.scene.update_render()
        ee_position = np.asarray(self.ee_link.get_pose().p, dtype=np.float64)
        return ee_position, float(np.linalg.norm(state.target - ee_position))

    def render_rgb(self) -> np.ndarray:
        self.camera.take_picture()
        rgba = self.camera.get_picture("Color")
        if self.viewer is not None and not self.viewer.closed:
            self.viewer.render()
        return (rgba[:, :, :3] * 255).clip(0, 255).astype(np.uint8)

    def close(self) -> None:
        if self.viewer is not None and not self.viewer.closed:
            self.viewer.close()

    def _find_link(self, name: str) -> sapien.Link:
        for link in self.robot.get_links():
            if link.get_name() == name:
                return link
        link_names = ", ".join(link.get_name() for link in self.robot.get_links())
        raise ValueError(f"Cannot find link {name!r}; available links: {link_names}")

    def _add_workcell(self) -> None:
        add_box(
            self.scene,
            "tabletop",
            sapien.Pose([0.45, 0.0, -0.018], [1, 0, 0, 0]),
            (0.62, 0.44, 0.018),
            (0.72, 0.72, 0.68, 1.0),
        )

    def _create_viewer(self):
        from sapien.utils.viewer import Viewer

        viewer = Viewer(self.renderer)
        viewer.set_scene(self.scene)
        viewer.set_camera_xyz(1.45, -1.40, 1.05)
        viewer.set_camera_rpy(0.0, -0.52, 2.35)
        return viewer
