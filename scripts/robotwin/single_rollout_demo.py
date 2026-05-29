from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from common import PROJECT_ROOT, ensure_task_config, resolve_robotwin_root


@dataclass(frozen=True)
class RolloutResult:
    task_name: str
    success_count: int
    test_count: int
    output_dir: Path
    result_file: Path
    viewer_file: Path
    video_file: Path | None


def _prepend_robotwin_paths(robotwin_root: Path) -> None:
    paths = [
        robotwin_root,
        robotwin_root / "policy",
        robotwin_root / "policy" / "DP",
        robotwin_root / "description" / "utils",
    ]
    for path in reversed(paths):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _copy_robotwin_eval_setup(
    *,
    task_name: str,
    task_config: str,
    ckpt_setting: str,
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    from envs import CONFIGS_PATH
    from script.eval_policy import get_camera_config, get_embodiment_config

    args = _load_yaml(Path("task_config") / f"{task_config}.yml")
    args["task_name"] = task_name
    args["task_config"] = task_config
    args["ckpt_setting"] = ckpt_setting

    embodiment_type = args.get("embodiment")
    embodiment_config_path = Path(CONFIGS_PATH) / "_embodiment_config.yml"
    embodiment_types = _load_yaml(embodiment_config_path)

    def get_embodiment_file(item: str) -> str:
        robot_file = embodiment_types[item]["file_path"]
        if robot_file is None:
            raise FileNotFoundError(f"Missing embodiment file for {item}")
        return robot_file

    camera_config_path = Path(CONFIGS_PATH) / "_camera_config.yml"
    camera_config = _load_yaml(camera_config_path)
    head_camera_type = args["camera"]["head_camera_type"]
    args["head_camera_h"] = camera_config[head_camera_type]["h"]
    args["head_camera_w"] = camera_config[head_camera_type]["w"]

    if len(embodiment_type) == 1:
        args["left_robot_file"] = get_embodiment_file(embodiment_type[0])
        args["right_robot_file"] = get_embodiment_file(embodiment_type[0])
        args["dual_arm_embodied"] = True
    elif len(embodiment_type) == 3:
        args["left_robot_file"] = get_embodiment_file(embodiment_type[0])
        args["right_robot_file"] = get_embodiment_file(embodiment_type[1])
        args["embodiment_dis"] = embodiment_type[2]
        args["dual_arm_embodied"] = False
    else:
        raise ValueError("embodiment must contain either 1 item or 3 items")

    args["left_embodiment_config"] = get_embodiment_config(args["left_robot_file"])
    args["right_embodiment_config"] = get_embodiment_config(args["right_robot_file"])
    args["eval_video_save_dir"] = output_dir
    args["eval_video_log"] = True

    camera_cfg = get_camera_config(args["camera"]["head_camera_type"])
    video_size = f"{camera_cfg['w']}x{camera_cfg['h']}"
    return args, camera_cfg, video_size


def _write_viewer(output_dir: Path, task_name: str, video_file: Path | None) -> Path:
    viewer_file = output_dir / "viewer.html"
    video_markup = "<p>尚未生成 rollout 视频。</p>"
    if video_file is not None:
        rel_video = video_file.name
        video_markup = (
            f'<video controls preload="metadata" src="{rel_video}" '
            'style="width: min(960px, 100%); background: #111;"></video>'
        )
    viewer_file.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RoboTwin 单次 Rollout - {task_name}</title>
  <style>
    body {{ font-family: sans-serif; margin: 32px; color: #17202a; background: #f7f8fa; }}
    main {{ max-width: 1040px; margin: 0 auto; }}
    h1 {{ font-size: 28px; margin-bottom: 8px; }}
    p {{ line-height: 1.6; }}
    .panel {{ background: white; border: 1px solid #d8dee8; padding: 20px; border-radius: 8px; }}
    code {{ background: #edf1f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>RoboTwin 单次 Rollout：{task_name}</h1>
  <p>该页面用于课程展示中的具身智能拓展部分。定量结果以官方 eval 为准，本页面只展示一次 policy rollout。</p>
  <section class="panel">
    {video_markup}
  </section>
  <p>结果文件：<code>_result.txt</code></p>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return viewer_file


def run_rollout(
    *,
    task_name: str,
    task_config: str,
    ckpt_setting: str,
    expert_data_num: int,
    seed: int,
    checkpoint_num: int,
    instruction_type: str,
    output_root: Path,
) -> RolloutResult:
    robotwin_root = resolve_robotwin_root()
    ensure_task_config(task_config, robotwin_root)
    _prepend_robotwin_paths(robotwin_root)

    original_cwd = Path.cwd()
    os.chdir(robotwin_root)
    try:
        from script.eval_policy import class_decorator, eval_function_decorator, eval_policy

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = output_root / task_name / f"{task_config}_seed{seed}_ckpt{checkpoint_num}_{stamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        args, _, video_size = _copy_robotwin_eval_setup(
            task_name=task_name,
            task_config=task_config,
            ckpt_setting=ckpt_setting,
            output_dir=output_dir,
        )
        args["policy_name"] = "DP"

        user_args: dict[str, Any] = {
            "policy_name": "DP",
            "task_name": task_name,
            "task_config": task_config,
            "ckpt_setting": ckpt_setting,
            "expert_data_num": expert_data_num,
            "seed": seed,
            "checkpoint_num": checkpoint_num,
            "instruction_type": instruction_type,
        }
        user_args["left_arm_dim"] = len(args["left_embodiment_config"]["arm_joints_name"][0])
        user_args["right_arm_dim"] = len(args["right_embodiment_config"]["arm_joints_name"][1])

        task_env = class_decorator(task_name)
        get_model = eval_function_decorator("DP", "get_model")
        model = get_model(user_args)
        start_seed = 100000 * (1 + seed)
        _, success_count = eval_policy(
            task_name,
            task_env,
            args,
            model,
            start_seed,
            test_num=1,
            video_size=video_size,
            instruction_type=instruction_type,
        )

        result_file = output_dir / "_result.txt"
        result_file.write_text(
            "\n".join(
                [
                    f"task_name: {task_name}",
                    f"policy_name: DP",
                    f"task_config: {task_config}",
                    f"ckpt_setting: {ckpt_setting}",
                    f"expert_data_num: {expert_data_num}",
                    f"seed: {seed}",
                    f"checkpoint_num: {checkpoint_num}",
                    f"single_rollout_success: {success_count}/1",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        video_file = output_dir / "episode0.mp4"
        if not video_file.is_file():
            video_file = None
        viewer_file = _write_viewer(output_dir, task_name, video_file)
        metadata_file = output_dir / "metadata.json"
        metadata_file.write_text(
            json.dumps(
                {
                    "task_name": task_name,
                    "task_config": task_config,
                    "ckpt_setting": ckpt_setting,
                    "expert_data_num": expert_data_num,
                    "seed": seed,
                    "checkpoint_num": checkpoint_num,
                    "success_count": success_count,
                    "video_file": str(video_file) if video_file else None,
                    "viewer_file": str(viewer_file),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return RolloutResult(task_name, success_count, 1, output_dir, result_file, viewer_file, video_file)
    finally:
        os.chdir(original_cwd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one RoboTwin DP rollout and write a local viewer.")
    parser.add_argument("--tasks", nargs="+", default=["grab_roller"])
    parser.add_argument("--task-config", default="demo_clean_smoke")
    parser.add_argument("--ckpt-setting", default="demo_clean_smoke")
    parser.add_argument("--expert-data-num", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--checkpoint-num", type=int, default=2)
    parser.add_argument("--instruction-type", default="unseen")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "robotwin" / "single_rollouts",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    results = [
        run_rollout(
            task_name=task_name,
            task_config=args.task_config,
            ckpt_setting=args.ckpt_setting,
            expert_data_num=args.expert_data_num,
            seed=args.seed,
            checkpoint_num=args.checkpoint_num,
            instruction_type=args.instruction_type,
            output_root=output_root,
        )
        for task_name in args.tasks
    ]
    for result in results:
        print(
            f"{result.task_name}: success={result.success_count}/{result.test_count} "
            f"viewer={result.viewer_file}"
        )


if __name__ == "__main__":
    main()
