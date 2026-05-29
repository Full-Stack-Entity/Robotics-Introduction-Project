from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROBOTWIN_ROOT = PROJECT_ROOT.parent / "RoboTwin-Project" / "RoboTwin"


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
