#!/usr/bin/env python3
"""Smoke-test RoboTwin core imports from the sibling checkout."""

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
    if not root.is_dir():
        raise FileNotFoundError(f"RoboTwin root not found: {root}")

    sys.path.insert(0, str(root))
    os.chdir(root)

    for module_name in (
        "sapien",
        "mplib",
        "torch",
        "cv2",
        "h5py",
        "envs._base_task",
        "envs.grab_roller",
        "envs.adjust_bottle",
        "envs.place_burger_fries",
        "script.collect_data",
    ):
        import_module(module_name)

    LOGGER.info("robotwin core imports ok: %s", root)


if __name__ == "__main__":
    main()
