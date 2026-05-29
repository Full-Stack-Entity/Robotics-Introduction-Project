#!/usr/bin/env python3
"""Verify that ffmpeg exposes a usable libx264 encoder."""

from __future__ import annotations

import logging
import subprocess


LOGGER = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-h", "encoder=libx264"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    output = result.stdout
    if result.returncode != 0:
        raise RuntimeError(output)
    if "Encoder libx264" not in output or "-crf" not in output:
        raise RuntimeError("ffmpeg exists but libx264 encoder support was not detected")
    LOGGER.info("ffmpeg libx264 backend ok")


if __name__ == "__main__":
    main()
