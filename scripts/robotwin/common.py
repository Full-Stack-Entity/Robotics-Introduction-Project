from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROBOTWIN_ROOT = PROJECT_ROOT.parent / "RoboTwin-Project" / "RoboTwin"
DEFAULT_ARTIFACT_ROOT = PROJECT_ROOT / "outputs" / "robotwin" / "artifacts"


def resolve_robotwin_root() -> Path:
    root = Path(os.environ.get("ROBOTWIN_ROOT", DEFAULT_ROBOTWIN_ROOT)).expanduser()
    root = root.resolve()
    if not (root / "script" / "collect_data.py").is_file():
        raise FileNotFoundError(f"RoboTwin root is invalid: {root}")
    return root


def ensure_task_config(config_name: str, robotwin_root: Path | None = None) -> Path:
    robotwin_root = robotwin_root or resolve_robotwin_root()
    source = PROJECT_ROOT / "configs" / "robotwin" / f"{config_name}.yml"
    target = robotwin_root / "task_config" / f"{config_name}.yml"
    if not source.is_file():
        if target.is_file():
            return target
        raise FileNotFoundError(f"Missing project config: {source}")
    if not target.is_file() or source.read_bytes() != target.read_bytes():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return target


def resolve_artifact_root() -> Path:
    root = Path(os.environ.get("ROBOTWIN_ARTIFACT_ROOT", DEFAULT_ARTIFACT_ROOT)).expanduser()
    return root.resolve()


def _link_or_migrate_directory(link_path: Path, target_path: Path) -> Path:
    target_path = target_path.resolve()
    if link_path.is_symlink():
        current_target = link_path.resolve()
        if current_target != target_path:
            raise FileExistsError(f"{link_path} already points to {current_target}, not {target_path}")
        target_path.mkdir(parents=True, exist_ok=True)
        return target_path

    if link_path.exists():
        if target_path.exists():
            raise FileExistsError(
                f"Both source and target exist; refusing to merge automatically: {link_path} -> {target_path}"
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(link_path), str(target_path))
    else:
        target_path.mkdir(parents=True, exist_ok=True)

    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.symlink_to(target_path, target_is_directory=True)
    return target_path


def ensure_robotwin_artifact_links(
    *,
    robotwin_root: Path | None = None,
    tasks: Sequence[str] = (),
    task_configs: Sequence[str] = (),
    link_data: bool = False,
    link_dp_data: bool = False,
    link_checkpoints: bool = False,
    link_eval: bool = False,
) -> Path:
    robotwin_root = robotwin_root or resolve_robotwin_root()
    artifact_root = resolve_artifact_root()
    artifact_root.mkdir(parents=True, exist_ok=True)

    if link_data:
        for task_name in tasks:
            for task_config in task_configs:
                _link_or_migrate_directory(
                    robotwin_root / "data" / task_name / task_config,
                    artifact_root / "data" / task_name / task_config,
                )

    if link_dp_data:
        _link_or_migrate_directory(
            robotwin_root / "policy" / "DP" / "data",
            artifact_root / "dp_data",
        )

    if link_checkpoints:
        _link_or_migrate_directory(
            robotwin_root / "policy" / "DP" / "checkpoints",
            artifact_root / "checkpoints",
        )

    if link_eval:
        for task_name in tasks:
            _link_or_migrate_directory(
                robotwin_root / "eval_result" / task_name,
                artifact_root / "eval_result" / task_name,
            )

    return artifact_root


def run_command(
    cmd: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    printable = " ".join(cmd)
    print(f"[run] cwd={cwd}", flush=True)
    print(f"[run] {printable}", flush=True)
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        env=merged_env,
        timeout=timeout,
        check=True,
        text=True,
    )


def python_executable() -> str:
    return sys.executable


def latest_directory(root: Path) -> Path | None:
    if not root.exists():
        return None
    dirs = [path for path in root.iterdir() if path.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda path: path.stat().st_mtime)
