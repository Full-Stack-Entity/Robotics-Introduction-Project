#!/usr/bin/env python3
"""Write a reproducibility-oriented environment report for the course project."""

from __future__ import annotations

import importlib
import platform
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "outputs" / "environment.md"


def command_output(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip() if result.stdout.strip() else f"exit code {result.returncode}"


def module_version(name: str) -> str:
    try:
        module = importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001 - report exact import failure for reproducibility.
        return f"import failed: {type(exc).__name__}: {exc}"
    version = getattr(module, "__version__", None)
    return str(version) if version is not None else "import ok, no __version__"


def main() -> None:
    robotwin_root = (PROJECT_ROOT / "../RoboTwin-Project/RoboTwin").resolve()
    lines = [
        "# Environment Report",
        "",
        "## System",
        f"- Python: `{sys.version.replace(chr(10), ' ')}`",
        f"- Platform: `{platform.platform()}`",
        f"- Machine: `{platform.machine()}`",
        "",
        "## GPU",
        "```text",
        command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
        "```",
        "",
        "## Pixi",
        "```text",
        command_output(["pixi", "--version"]),
        "```",
        "",
        "## Key Python Modules",
    ]

    for module_name in (
        "numpy",
        "torch",
        "torchvision",
        "sapien",
        "mplib",
        "cv2",
        "h5py",
        "zarr",
        "hydra",
        "diffusers",
        "wandb",
    ):
        lines.append(f"- `{module_name}`: `{module_version(module_name)}`")

    lines.extend(
        [
            "",
            "## RoboTwin Checkout",
            f"- Path: `{robotwin_root}`",
            "```text",
            command_output(["git", "status", "--short", "--branch"], cwd=robotwin_root),
            "```",
            "",
            "## Course Project Checkout",
            "```text",
            command_output(["git", "status", "--short", "--branch"], cwd=PROJECT_ROOT),
            "```",
            "",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
