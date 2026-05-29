from __future__ import annotations

import argparse

from common import ensure_robotwin_artifact_links, resolve_artifact_root, resolve_robotwin_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move RoboTwin-generated artifacts into this course project and keep RoboTwin path symlinks."
    )
    parser.add_argument("--tasks", nargs="+", default=[])
    parser.add_argument("--task-configs", nargs="+", default=[])
    parser.add_argument("--link-data", action="store_true")
    parser.add_argument("--link-dp-data", action="store_true")
    parser.add_argument("--link-checkpoints", action="store_true")
    parser.add_argument("--link-eval", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    robotwin_root = resolve_robotwin_root()
    artifact_root = ensure_robotwin_artifact_links(
        robotwin_root=robotwin_root,
        tasks=args.tasks,
        task_configs=args.task_configs,
        link_data=args.link_data,
        link_dp_data=args.link_dp_data,
        link_checkpoints=args.link_checkpoints,
        link_eval=args.link_eval,
    )
    print(f"[artifact] robotwin_root={robotwin_root}")
    print(f"[artifact] artifact_root={artifact_root}")
    print(f"[artifact] env ROBOTWIN_ARTIFACT_ROOT default={resolve_artifact_root()}")


if __name__ == "__main__":
    main()
