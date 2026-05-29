#!/usr/bin/env python3
"""Render Phase 1 SAPIEN tasks with a real Franka Panda robot."""

from __future__ import annotations

import argparse
import logging
import time
from dataclasses import replace
from pathlib import Path

import imageio.v2 as imageio

from franka_scene import FrankaSapienScene
from kinematics import FrankaIKSolver, RobotState, TaskSpec, build_task_specs, default_franka_config
from live_preview import LivePreviewServer
from reporting import OutputLayout, write_csv, write_plot, write_summary, write_viewer


LOGGER = logging.getLogger(__name__)
DEFAULT_TASKS = ("six_points", "figure_eight", "ellipse")


def render_task(
    spec: TaskSpec,
    states: list[RobotState],
    scene: FrankaSapienScene,
    output: OutputLayout,
    fps: int,
    save_keyframes: bool,
    live: LivePreviewServer | None,
    preview_delay: float,
) -> dict[str, str]:
    csv_path = output.logs / f"{spec.name}_trajectory.csv"
    plot_path = output.plots / f"{spec.name}_trajectory.png"
    video_path = output.videos / f"{spec.name}.mp4"
    frame_dir = output.frames / spec.name
    if save_keyframes:
        frame_dir.mkdir(parents=True, exist_ok=True)

    scene.add_task_guides(spec)
    key_indices = set(spec.key_indices)
    rendered_states: list[RobotState] = []
    with imageio.get_writer(video_path, fps=fps, codec="libx264", quality=8, macro_block_size=1) as writer:
        for state in states:
            ee_position, error = scene.set_state(state)
            rendered_state = replace(state, ee_position=ee_position, error=error)
            rendered_states.append(rendered_state)
            image = scene.render_rgb()
            writer.append_data(image)
            if live is not None:
                live.update(image)
            if save_keyframes and state.index in key_indices:
                imageio.imwrite(frame_dir / f"key_{state.index:04d}.png", image)
            if preview_delay > 0:
                time.sleep(preview_delay)

    write_csv(csv_path, rendered_states)
    write_plot(plot_path, spec, rendered_states)
    max_error = max(state.error for state in rendered_states)
    LOGGER.info("%s: frames=%d max_error=%.6f video=%s", spec.name, len(states), max_error, video_path)
    return {
        "name": spec.name,
        "title_zh": spec.title_zh,
        "title_en": spec.title_en,
        "frames": str(len(states)),
        "max_error_m": f"{max_error:.8f}",
        "csv": str(csv_path),
        "plot": str(plot_path),
        "video": str(video_path),
        "keyframes": str(frame_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", nargs="+", default=list(DEFAULT_TASKS), help="Tasks to render")
    parser.add_argument("--output-root", type=Path, default=Path("outputs/sapien"))
    parser.add_argument("--steps-per-segment", type=int, default=36)
    parser.add_argument("--curve-steps", type=int, default=180)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--no-keyframes", action="store_true")
    parser.add_argument("--live-browser", action="store_true", help="Serve an MJPEG browser preview while rendering")
    parser.add_argument("--live-host", default="127.0.0.1")
    parser.add_argument("--live-port", type=int, default=8001)
    parser.add_argument("--live-startup-wait", type=float, default=1.0)
    parser.add_argument("--preview-delay", type=float, default=0.0)
    parser.add_argument("--sapien-viewer", action="store_true", help="Also open the native SAPIEN viewer")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")
    output = OutputLayout.from_root(args.output_root)
    output.ensure()

    franka_cfg = default_franka_config()
    specs = build_task_specs(args.tasks, args.steps_per_segment, args.curve_steps)

    solver = FrankaIKSolver(franka_cfg)
    solved_states = {spec.name: solver.solve_task(spec, fps=args.fps) for spec in specs}
    live = LivePreviewServer(args.live_host, args.live_port) if args.live_browser else None
    if live is not None:
        live.start()
        LOGGER.info("请在浏览器打开：%s", live.url)
        time.sleep(max(args.live_startup_wait, 0.0))

    artifacts: list[dict[str, str]] = []
    try:
        for spec in specs:
            scene = FrankaSapienScene(franka_cfg, width=args.width, height=args.height, sapien_viewer=args.sapien_viewer)
            try:
                artifacts.append(
                    render_task(
                        spec=spec,
                        states=solved_states[spec.name],
                        scene=scene,
                        output=output,
                        fps=args.fps,
                        save_keyframes=not args.no_keyframes,
                        live=live,
                        preview_delay=args.preview_delay,
                    )
                )
            finally:
                scene.close()
    finally:
        if live is not None:
            live.close()

    write_viewer(output.root / "viewer.html", artifacts)
    write_summary(output.root / "summary.md", artifacts)
    LOGGER.info("wrote %s", output.root / "viewer.html")
    LOGGER.info("wrote %s", output.root / "summary.md")


if __name__ == "__main__":
    main()
