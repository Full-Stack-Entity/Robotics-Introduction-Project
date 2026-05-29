from __future__ import annotations

import argparse
import subprocess

from common import (
    PROJECT_ROOT,
    ensure_task_config,
    latest_directory,
    python_executable,
    resolve_robotwin_root,
    run_command,
)


DEFAULT_TASK = "grab_roller"
DEFAULT_CONFIG = "demo_clean_smoke"
DEFAULT_EPISODES = 5
DEFAULT_SEED = 0
DEFAULT_CHECKPOINT = 2


def collect_data(args: argparse.Namespace) -> None:
    robotwin_root = resolve_robotwin_root()
    ensure_task_config(args.task_config, robotwin_root)
    run_command(
        ["bash", "collect_data.sh", args.task_name, args.task_config, str(args.gpu_id)],
        cwd=robotwin_root,
        env={"CUDA_VISIBLE_DEVICES": str(args.gpu_id)},
    )


def process_data(args: argparse.Namespace) -> None:
    robotwin_root = resolve_robotwin_root()
    ensure_task_config(args.task_config, robotwin_root)
    run_command(
        [
            python_executable(),
            "process_data.py",
            args.task_name,
            args.task_config,
            str(args.expert_data_num),
        ],
        cwd=robotwin_root / "policy" / "DP",
    )


def train_debug(args: argparse.Namespace) -> None:
    robotwin_root = resolve_robotwin_root()
    ensure_task_config(args.task_config, robotwin_root)
    output_dir = f"data/outputs/{args.task_name}_dp_smoke_seed{args.seed}"
    zarr_path = f"data/{args.task_name}-{args.task_config}-{args.expert_data_num}.zarr"
    cmd = [
        python_executable(),
        "train.py",
        "--config-name=robot_dp_14.yaml",
        f"task.name={args.task_name}",
        f"task.dataset.zarr_path={zarr_path}",
        "training.debug=True",
        "training.resume=False",
        f"training.seed={args.seed}",
        "training.device=cuda:0",
        "training.use_ema=False",
        "dataloader.batch_size=16",
        "val_dataloader.batch_size=16",
        "policy.num_inference_steps=4",
        "policy.noise_scheduler.num_train_timesteps=20",
        f"exp_name={args.task_name}-robot_dp-smoke",
        "logging.mode=offline",
        f"setting={args.task_config}",
        f"expert_data_num={args.expert_data_num}",
        "head_camera_type=D435",
        f"hydra.run.dir={output_dir}",
    ]
    run_command(cmd, cwd=robotwin_root / "policy" / "DP", env={"CUDA_VISIBLE_DEVICES": str(args.gpu_id)})


def eval_start(args: argparse.Namespace) -> None:
    robotwin_root = resolve_robotwin_root()
    ensure_task_config(args.task_config, robotwin_root)
    eval_root = (
        robotwin_root
        / "eval_result"
        / args.task_name
        / "DP"
        / args.task_config
        / args.ckpt_setting
    )
    latest_before = latest_directory(eval_root)
    cmd = [
        python_executable(),
        "script/eval_policy.py",
        "--config",
        "policy/DP/deploy_policy.yml",
        "--overrides",
        "--task_name",
        args.task_name,
        "--task_config",
        args.task_config,
        "--ckpt_setting",
        args.ckpt_setting,
        "--expert_data_num",
        str(args.expert_data_num),
        "--seed",
        str(args.seed),
        "--checkpoint_num",
        str(args.checkpoint_num),
    ]
    try:
        run_command(
            cmd,
            cwd=robotwin_root,
            env={"CUDA_VISIBLE_DEVICES": str(args.gpu_id)},
            timeout=args.eval_timeout,
        )
    except subprocess.TimeoutExpired:
        latest = latest_directory(eval_root)
        if latest is None or latest == latest_before:
            raise
        print(f"[eval-start] timed out after {args.eval_timeout}s; latest eval dir: {latest}")
        print("[eval-start] This still confirms the official eval entry can start and write artifacts.")


def single_rollout(args: argparse.Namespace) -> None:
    robotwin_root = resolve_robotwin_root()
    ensure_task_config(args.task_config, robotwin_root)
    output_root = PROJECT_ROOT / "outputs" / "robotwin" / "single_rollouts"
    cmd = [
        python_executable(),
        str(PROJECT_ROOT / "scripts" / "robotwin" / "single_rollout_demo.py"),
        "--tasks",
        args.task_name,
        "--task-config",
        args.task_config,
        "--ckpt-setting",
        args.ckpt_setting,
        "--expert-data-num",
        str(args.expert_data_num),
        "--seed",
        str(args.seed),
        "--checkpoint-num",
        str(args.checkpoint_num),
        "--output-root",
        str(output_root),
    ]
    run_command(cmd, cwd=PROJECT_ROOT, env={"CUDA_VISIBLE_DEVICES": str(args.gpu_id)})


def run_all_light(args: argparse.Namespace) -> None:
    collect_data(args)
    process_data(args)
    train_debug(args)
    eval_start(args)
    single_rollout(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lightweight RoboTwin DP smoke stages.")
    parser.add_argument(
        "stage",
        choices=["collect", "process", "train-debug", "eval-start", "single-rollout", "all-light"],
    )
    parser.add_argument("--task-name", default=DEFAULT_TASK)
    parser.add_argument("--task-config", default=DEFAULT_CONFIG)
    parser.add_argument("--ckpt-setting", default=DEFAULT_CONFIG)
    parser.add_argument("--expert-data-num", type=int, default=DEFAULT_EPISODES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--checkpoint-num", type=int, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--gpu-id", default="0")
    parser.add_argument("--eval-timeout", type=float, default=90.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.stage == "collect":
        collect_data(args)
    elif args.stage == "process":
        process_data(args)
    elif args.stage == "train-debug":
        train_debug(args)
    elif args.stage == "eval-start":
        eval_start(args)
    elif args.stage == "single-rollout":
        single_rollout(args)
    elif args.stage == "all-light":
        run_all_light(args)
    else:
        raise ValueError(args.stage)


if __name__ == "__main__":
    main()
