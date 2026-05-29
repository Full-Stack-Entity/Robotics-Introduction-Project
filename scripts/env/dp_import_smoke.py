#!/usr/bin/env python3
"""Smoke-test RoboTwin Diffusion Policy imports."""

from __future__ import annotations

import importlib
import logging
import os
from pathlib import Path
import sys


LOGGER = logging.getLogger(__name__)


def robotwin_root() -> Path:
    configured = os.environ.get("ROBOTWIN_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path(__file__).resolve().parents[2] / "../RoboTwin-Project/RoboTwin").resolve()


def import_module(name: str) -> None:
    importlib.import_module(name)
    LOGGER.info("import ok: %s", name)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    root = robotwin_root()
    dp_root = root / "policy" / "DP"
    if not dp_root.is_dir():
        raise FileNotFoundError(f"RoboTwin DP root not found: {dp_root}")

    sys.path.insert(0, str(root))
    sys.path.insert(0, str(dp_root))
    os.chdir(dp_root)

    for module_name in (
        "hydra",
        "omegaconf",
        "zarr",
        "numba",
        "dill",
        "diffusers",
        "wandb",
        "diffusion_policy.workspace.robotworkspace",
        "diffusion_policy.dataset.robot_image_dataset",
        "diffusion_policy.policy.diffusion_unet_image_policy",
        "dp_model",
    ):
        import_module(module_name)

    LOGGER.info("robotwin DP imports ok: %s", dp_root)


if __name__ == "__main__":
    main()
