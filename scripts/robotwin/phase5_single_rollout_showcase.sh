#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Phase 5 single-rollout showcase for three final DP checkpoints.

This script does NOT run the official 100-trial eval. It only runs one policy
rollout per task for presentation, saves mp4 videos, writes local HTML viewers,
and can serve the generated viewer pages over HTTP.

Default run:
  pixi run robotwin-phase5-single-rollout

Browser-served run:
  WEB_SERVER=1 OPEN_BROWSER=1 pixi run robotwin-phase5-single-rollout

Native SAPIEN viewer run:
  SAPIEN_VIEWER=1 RENDER_FREQ=1 pixi run robotwin-phase5-single-rollout

Dry run without model rollout:
  DRY_RUN=1 pixi run robotwin-phase5-single-rollout

Environment overrides:
  TASKS="grab_roller adjust_bottle place_burger_fries"
  TASK_CONFIG=demo_clean_100
  CKPT_SETTING=demo_clean_100
  EXPERT_DATA_NUM=100
  SEED=0
  CHECKPOINT_NUM=100
  GPU_ID=0
  INSTRUCTION_TYPE=unseen
  ROBOTWIN_ROOT=../RoboTwin-Project/RoboTwin
  ROBOTWIN_ARTIFACT_ROOT=outputs/robotwin/artifacts
  ROLLOUT_ROOT=outputs/robotwin/single_rollouts/showcase_<timestamp>
  LOG_ROOT=outputs/robotwin/logs/phase5_single_rollout_<timestamp>
  DRY_RUN=0

Viewing options:
  WEB_SERVER=1       Start a local HTTP server rooted at ROLLOUT_ROOT.
  WEB_HOST=127.0.0.1 HTTP bind host.
  WEB_PORT=8002      HTTP port.
  OPEN_BROWSER=1     Open the HTTP URL when WEB_SERVER=1, else open index.html.
  KEEP_SERVER=1      Keep the HTTP server running after rollout completion.

Native SAPIEN options:
  SAPIEN_VIEWER=1    Generate a temporary task config with render_freq enabled.
  RENDER_FREQ=1      Render every N control steps in the native SAPIEN viewer.

Outputs:
  ROLLOUT_ROOT/index.html
  ROLLOUT_ROOT/manifest.json
  ROLLOUT_ROOT/<task>/<task_config>_seed<seed>_ckpt<ckpt>_<timestamp>/
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  show_help
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ROBOTWIN_ROOT="${ROBOTWIN_ROOT:-${PROJECT_ROOT}/../RoboTwin-Project/RoboTwin}"
ROBOTWIN_ARTIFACT_ROOT="${ROBOTWIN_ARTIFACT_ROOT:-${PROJECT_ROOT}/outputs/robotwin/artifacts}"
TASKS="${TASKS:-grab_roller adjust_bottle place_burger_fries}"
TASK_CONFIG="${TASK_CONFIG:-demo_clean_100}"
CKPT_SETTING="${CKPT_SETTING:-${TASK_CONFIG}}"
EXPERT_DATA_NUM="${EXPERT_DATA_NUM:-100}"
SEED="${SEED:-0}"
CHECKPOINT_NUM="${CHECKPOINT_NUM:-100}"
GPU_ID="${GPU_ID:-0}"
INSTRUCTION_TYPE="${INSTRUCTION_TYPE:-unseen}"
SAPIEN_VIEWER="${SAPIEN_VIEWER:-0}"
if [[ "${SAPIEN_VIEWER}" == "1" ]]; then
  RENDER_FREQ="${RENDER_FREQ:-1}"
else
  RENDER_FREQ="${RENDER_FREQ:-0}"
fi
WEB_SERVER="${WEB_SERVER:-0}"
WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-8002}"
OPEN_BROWSER="${OPEN_BROWSER:-0}"
KEEP_SERVER="${KEEP_SERVER:-${WEB_SERVER}}"
DRY_RUN="${DRY_RUN:-0}"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_ROOT="${LOG_ROOT:-${PROJECT_ROOT}/outputs/robotwin/logs/phase5_single_rollout_${STAMP}}"
ROLLOUT_ROOT="${ROLLOUT_ROOT:-${PROJECT_ROOT}/outputs/robotwin/single_rollouts/showcase_${STAMP}}"
RUN_TASK_CONFIG="${TASK_CONFIG}"
export ROBOTWIN_ROOT ROBOTWIN_ARTIFACT_ROOT

read -r -a TASK_LIST <<< "${TASKS}"

require_file() {
  local path="$1"
  if [[ ! -f "${path}" ]]; then
    echo "[error] missing required file: ${path}" >&2
    exit 2
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "${path}" ]]; then
    echo "[error] missing required directory: ${path}" >&2
    exit 2
  fi
}

copy_project_config_if_present() {
  local source="${PROJECT_ROOT}/configs/robotwin/${TASK_CONFIG}.yml"
  local target="${ROBOTWIN_ROOT}/task_config/${TASK_CONFIG}.yml"
  if [[ -f "${source}" ]]; then
    mkdir -p "$(dirname "${target}")"
    cp "${source}" "${target}"
  fi
  require_file "${target}"
}

prepare_showcase_config() {
  RUN_TASK_CONFIG="${TASK_CONFIG}"
  if [[ "${SAPIEN_VIEWER}" != "1" ]]; then
    copy_project_config_if_present
    return
  fi

  RUN_TASK_CONFIG="${TASK_CONFIG}_showcase_render${RENDER_FREQ}"
  RUN_TASK_CONFIG="${RUN_TASK_CONFIG}" python - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

import yaml

project_root = Path(os.environ["PROJECT_ROOT"])
robotwin_root = Path(os.environ["ROBOTWIN_ROOT"])
task_config = os.environ["TASK_CONFIG"]
run_task_config = os.environ["RUN_TASK_CONFIG"]
render_freq = int(os.environ["RENDER_FREQ"])

source = project_root / "configs" / "robotwin" / f"{task_config}.yml"
if not source.is_file():
    source = robotwin_root / "task_config" / f"{task_config}.yml"
if not source.is_file():
    raise FileNotFoundError(f"Cannot find source task config for {task_config}")

config = yaml.safe_load(source.read_text(encoding="utf-8"))
config["render_freq"] = render_freq
config["eval_video_log"] = True

project_target = project_root / "outputs" / "robotwin" / "artifacts" / "generated_configs" / f"{run_task_config}.yml"
robotwin_target = robotwin_root / "task_config" / f"{run_task_config}.yml"
for target in (project_target, robotwin_target):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")

print(f"[config] generated {project_target}")
print(f"[config] generated {robotwin_target}")
PY
}

write_run_index() {
  TASKS_JSON="$(printf '%s\n' "${TASK_LIST[@]}" | python -c 'import json,sys; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))')"
  TASKS_JSON="${TASKS_JSON}" python - <<'PY'
from __future__ import annotations

import html
import json
import os
from pathlib import Path

root = Path(os.environ["ROLLOUT_ROOT"]).resolve()
tasks = json.loads(os.environ["TASKS_JSON"])
manifest = {
    "rollout_root": str(root),
    "task_config": os.environ["RUN_TASK_CONFIG"],
    "ckpt_setting": os.environ["CKPT_SETTING"],
    "checkpoint_num": int(os.environ["CHECKPOINT_NUM"]),
    "seed": int(os.environ["SEED"]),
    "instruction_type": os.environ["INSTRUCTION_TYPE"],
    "sapien_viewer": os.environ["SAPIEN_VIEWER"] == "1",
    "render_freq": int(os.environ["RENDER_FREQ"]),
    "tasks": [],
}

cards = []
for task in tasks:
    task_root = root / task
    dirs = [path for path in task_root.iterdir() if path.is_dir()] if task_root.is_dir() else []
    latest = max(dirs, key=lambda path: path.stat().st_mtime) if dirs else None
    if latest is None:
        manifest["tasks"].append({"task": task, "status": "missing"})
        cards.append(f"<section><h2>{html.escape(task)}</h2><p>Missing rollout directory.</p></section>")
        continue

    viewer = latest / "viewer.html"
    video = latest / "episode0.mp4"
    result = latest / "_result.txt"
    rel_viewer = viewer.relative_to(root).as_posix() if viewer.exists() else ""
    rel_video = video.relative_to(root).as_posix() if video.exists() else ""
    rel_result = result.relative_to(root).as_posix() if result.exists() else ""
    manifest["tasks"].append(
        {
            "task": task,
            "status": "ok",
            "directory": str(latest),
            "viewer": str(viewer) if viewer.exists() else None,
            "video": str(video) if video.exists() else None,
            "result": str(result) if result.exists() else None,
        }
    )
    video_html = (
        f'<video controls preload="metadata" src="{html.escape(rel_video)}"></video>'
        if rel_video
        else "<p>No video file found.</p>"
    )
    cards.append(
        f"""
<section>
  <h2>{html.escape(task)}</h2>
  {video_html}
  <p>
    <a href="{html.escape(rel_viewer)}">viewer.html</a>
    {' | <a href="' + html.escape(rel_result) + '">_result.txt</a>' if rel_result else ''}
  </p>
</section>
"""
    )

(root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
(root / "index.html").write_text(
    f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RoboTwin Phase 5 单次 Rollout 展示</title>
  <style>
    body {{ margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #17202a; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 28px; }}
    header {{ margin-bottom: 18px; }}
    section {{ background: white; border: 1px solid #d8dee8; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    video {{ width: min(960px, 100%); background: #10151c; display: block; border-radius: 6px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    a {{ color: #0b63ce; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>RoboTwin Phase 5 单次 Rollout 展示</h1>
    <p>每个任务只运行一次 rollout。官方 100 次 eval 不在本脚本中执行。</p>
    <p>Checkpoint: <code>{html.escape(os.environ["CKPT_SETTING"])}/{html.escape(os.environ["CHECKPOINT_NUM"])}</code>;
    Task config: <code>{html.escape(os.environ["RUN_TASK_CONFIG"])}</code>.</p>
  </header>
  {''.join(cards)}
</main>
</body>
</html>
""",
    encoding="utf-8",
)
print(root / "index.html")
print(root / "manifest.json")
PY
}

start_web_server() {
  if [[ "${WEB_SERVER}" != "1" ]]; then
    return
  fi
  (
    cd "${ROLLOUT_ROOT}"
    python -m http.server "${WEB_PORT}" --bind "${WEB_HOST}"
  ) &
  SERVER_PID="$!"
  trap 'kill "${SERVER_PID}" 2>/dev/null || true' EXIT INT TERM
  echo "[web] serving ${ROLLOUT_ROOT}"
  echo "[web] open http://${WEB_HOST}:${WEB_PORT}/index.html"
}

open_viewer() {
  local target="$1"
  if [[ "${OPEN_BROWSER}" != "1" ]]; then
    return
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${target}" >/dev/null 2>&1 || true
  else
    echo "[web] xdg-open not found; open manually: ${target}"
  fi
}

require_dir "${ROBOTWIN_ROOT}"
require_file "${ROBOTWIN_ROOT}/script/eval_policy.py"
require_file "${PROJECT_ROOT}/scripts/robotwin/single_rollout_demo.py"
mkdir -p "${LOG_ROOT}" "${ROLLOUT_ROOT}"
export PROJECT_ROOT TASK_CONFIG RUN_TASK_CONFIG RENDER_FREQ ROLLOUT_ROOT CKPT_SETTING CHECKPOINT_NUM SEED INSTRUCTION_TYPE SAPIEN_VIEWER

prepare_showcase_config
export RUN_TASK_CONFIG

python "${PROJECT_ROOT}/scripts/robotwin/prepare_artifact_links.py" \
  --tasks "${TASK_LIST[@]}" \
  --task-configs "${TASK_CONFIG}" \
  --link-dp-data \
  --link-checkpoints

{
  echo "phase: 5-single-rollout-showcase"
  echo "timestamp: ${STAMP}"
  echo "project_root: ${PROJECT_ROOT}"
  echo "robotwin_root: ${ROBOTWIN_ROOT}"
  echo "artifact_root: ${ROBOTWIN_ARTIFACT_ROOT}"
  echo "task_config: ${RUN_TASK_CONFIG}"
  echo "ckpt_setting: ${CKPT_SETTING}"
  echo "expert_data_num: ${EXPERT_DATA_NUM}"
  echo "seed: ${SEED}"
  echo "checkpoint_num: ${CHECKPOINT_NUM}"
  echo "gpu_id: ${GPU_ID}"
  echo "instruction_type: ${INSTRUCTION_TYPE}"
  echo "sapien_viewer: ${SAPIEN_VIEWER}"
  echo "render_freq: ${RENDER_FREQ}"
  echo "web_server: ${WEB_SERVER}"
  echo "dry_run: ${DRY_RUN}"
  echo "rollout_root: ${ROLLOUT_ROOT}"
  echo "tasks: ${TASKS}"
} | tee "${LOG_ROOT}/run_env.txt"

for task_name in "${TASK_LIST[@]}"; do
  ckpt_file="${ROBOTWIN_ARTIFACT_ROOT}/checkpoints/${task_name}-${CKPT_SETTING}-${EXPERT_DATA_NUM}-${SEED}/${CHECKPOINT_NUM}.ckpt"
  require_file "${ckpt_file}"
done

if [[ "${DRY_RUN}" == "1" ]]; then
  echo
  echo "[dry-run] Would run one rollout per task with:"
  printf '  CUDA_VISIBLE_DEVICES=%s python scripts/robotwin/single_rollout_demo.py' "${GPU_ID}"
  printf ' --tasks'
  printf ' %q' "${TASK_LIST[@]}"
  printf ' --task-config %q' "${RUN_TASK_CONFIG}"
  printf ' --ckpt-setting %q' "${CKPT_SETTING}"
  printf ' --expert-data-num %q' "${EXPERT_DATA_NUM}"
  printf ' --seed %q' "${SEED}"
  printf ' --checkpoint-num %q' "${CHECKPOINT_NUM}"
  printf ' --instruction-type %q' "${INSTRUCTION_TYPE}"
  printf ' --output-root %q\n' "${ROLLOUT_ROOT}"
  echo "[dry-run] Official 100-trial eval is not invoked by this script."
  exit 0
fi

start_web_server

echo
echo "========== Phase 5 single-rollout showcase =========="
rollout_log="${LOG_ROOT}/single_rollout_showcase.log"
(
  cd "${PROJECT_ROOT}"
  CUDA_VISIBLE_DEVICES="${GPU_ID}" \
    python scripts/robotwin/single_rollout_demo.py \
      --tasks "${TASK_LIST[@]}" \
      --task-config "${RUN_TASK_CONFIG}" \
      --ckpt-setting "${CKPT_SETTING}" \
      --expert-data-num "${EXPERT_DATA_NUM}" \
      --seed "${SEED}" \
      --checkpoint-num "${CHECKPOINT_NUM}" \
      --instruction-type "${INSTRUCTION_TYPE}" \
      --output-root "${ROLLOUT_ROOT}"
) 2>&1 | tee "${rollout_log}"

write_run_index | tee "${LOG_ROOT}/viewer_index.log"

index_file="${ROLLOUT_ROOT}/index.html"
if [[ "${WEB_SERVER}" == "1" ]]; then
  open_viewer "http://${WEB_HOST}:${WEB_PORT}/index.html"
else
  open_viewer "${index_file}"
fi

echo
echo "[done] Single-rollout showcase finished."
echo "[artifact] offline index: ${index_file}"
echo "[artifact] manifest: ${ROLLOUT_ROOT}/manifest.json"
echo "[artifact] logs: ${LOG_ROOT}"
if [[ "${WEB_SERVER}" == "1" ]]; then
  echo "[artifact] web index: http://${WEB_HOST}:${WEB_PORT}/index.html"
fi

if [[ "${WEB_SERVER}" == "1" && "${KEEP_SERVER}" == "1" ]]; then
  echo "[web] Press Ctrl+C to stop the HTTP server."
  wait "${SERVER_PID}"
fi
