#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Phase 3: serial RoboTwin expert data generation for the course tasks.

Run from the course repo:
  pixi run robotwin-phase3-generate

Environment overrides:
  TASKS="grab_roller adjust_bottle place_burger_fries"
  TASK_CONFIG=demo_clean_100
  EXPERT_DATA_NUM=100
  GPU_ID=0
  ROBOTWIN_ROOT=../RoboTwin-Project/RoboTwin
  LOG_ROOT=outputs/robotwin/logs/phase3_<timestamp>

This is a heavy foreground command. It generates data serially and should be
run by the user, not by the agent.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  show_help
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ROBOTWIN_ROOT="${ROBOTWIN_ROOT:-${PROJECT_ROOT}/../RoboTwin-Project/RoboTwin}"
TASKS="${TASKS:-grab_roller adjust_bottle place_burger_fries}"
TASK_CONFIG="${TASK_CONFIG:-demo_clean_100}"
EXPERT_DATA_NUM="${EXPERT_DATA_NUM:-100}"
GPU_ID="${GPU_ID:-0}"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_ROOT="${LOG_ROOT:-${PROJECT_ROOT}/outputs/robotwin/logs/phase3_${STAMP}}"

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

prepare_config() {
  local source="${PROJECT_ROOT}/configs/robotwin/${TASK_CONFIG}.yml"
  local target="${ROBOTWIN_ROOT}/task_config/${TASK_CONFIG}.yml"
  if [[ -f "${source}" ]]; then
    mkdir -p "$(dirname "${target}")"
    cp "${source}" "${target}"
  fi
  require_file "${target}"
  python - "${target}" "${EXPERT_DATA_NUM}" <<'PY'
import sys
import yaml

path = sys.argv[1]
expected = int(sys.argv[2])
with open(path, "r", encoding="utf-8") as file:
    cfg = yaml.safe_load(file)
actual = int(cfg.get("episode_num", -1))
if actual != expected:
    raise SystemExit(
        f"[error] {path} has episode_num={actual}, but EXPERT_DATA_NUM={expected}. "
        "Set matching TASK_CONFIG/EXPERT_DATA_NUM values."
    )
PY
}

require_dir "${ROBOTWIN_ROOT}"
require_file "${ROBOTWIN_ROOT}/collect_data.sh"
prepare_config
mkdir -p "${LOG_ROOT}"

{
  echo "phase: 3"
  echo "timestamp: ${STAMP}"
  echo "project_root: ${PROJECT_ROOT}"
  echo "robotwin_root: ${ROBOTWIN_ROOT}"
  echo "task_config: ${TASK_CONFIG}"
  echo "expert_data_num: ${EXPERT_DATA_NUM}"
  echo "gpu_id: ${GPU_ID}"
  echo "tasks: ${TASKS}"
} | tee "${LOG_ROOT}/run_env.txt"

read -r -a TASK_LIST <<< "${TASKS}"
for task_name in "${TASK_LIST[@]}"; do
  echo
  echo "========== Phase 3 data generation: ${task_name} =========="
  task_log="${LOG_ROOT}/${task_name}_collect.log"
  (
    cd "${ROBOTWIN_ROOT}"
    CUDA_VISIBLE_DEVICES="${GPU_ID}" bash collect_data.sh "${task_name}" "${TASK_CONFIG}" "${GPU_ID}"
  ) 2>&1 | tee "${task_log}"

  data_dir="${ROBOTWIN_ROOT}/data/${task_name}/${TASK_CONFIG}/data"
  require_dir "${data_dir}"
  hdf5_count="$(find "${data_dir}" -maxdepth 1 -name 'episode*.hdf5' | wc -l)"
  if [[ "${hdf5_count}" -lt "${EXPERT_DATA_NUM}" ]]; then
    echo "[error] ${task_name}: expected ${EXPERT_DATA_NUM} HDF5 files, found ${hdf5_count}" >&2
    exit 3
  fi
  echo "[ok] ${task_name}: found ${hdf5_count} HDF5 files"
done

echo
echo "[done] Phase 3 data generation finished. Logs: ${LOG_ROOT}"
