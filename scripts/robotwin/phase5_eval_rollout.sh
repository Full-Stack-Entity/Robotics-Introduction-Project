#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Phase 5: serial official DP eval and custom single-rollout export.

Run from the course repo after Phase 4:
  pixi run robotwin-phase5-eval

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
  LOG_ROOT=outputs/robotwin/logs/phase5_<timestamp>

Official eval is the quantitative result. The custom rollout viewer is only for
PPT/video demonstration.
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
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_ROOT="${LOG_ROOT:-${PROJECT_ROOT}/outputs/robotwin/logs/phase5_${STAMP}}"
ROLLOUT_ROOT="${ROLLOUT_ROOT:-${PROJECT_ROOT}/outputs/robotwin/single_rollouts}"
export ROBOTWIN_ROOT ROBOTWIN_ARTIFACT_ROOT

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

require_dir "${ROBOTWIN_ROOT}"
require_file "${ROBOTWIN_ROOT}/script/eval_policy.py"
require_file "${PROJECT_ROOT}/scripts/robotwin/single_rollout_demo.py"
copy_project_config_if_present
mkdir -p "${LOG_ROOT}" "${ROLLOUT_ROOT}"
read -r -a TASK_LIST <<< "${TASKS}"
python "${PROJECT_ROOT}/scripts/robotwin/prepare_artifact_links.py" \
  --tasks "${TASK_LIST[@]}" \
  --task-configs "${TASK_CONFIG}" \
  --link-data \
  --link-dp-data \
  --link-checkpoints \
  --link-eval

{
  echo "phase: 5"
  echo "timestamp: ${STAMP}"
  echo "project_root: ${PROJECT_ROOT}"
  echo "robotwin_root: ${ROBOTWIN_ROOT}"
  echo "artifact_root: ${ROBOTWIN_ARTIFACT_ROOT}"
  echo "task_config: ${TASK_CONFIG}"
  echo "ckpt_setting: ${CKPT_SETTING}"
  echo "expert_data_num: ${EXPERT_DATA_NUM}"
  echo "seed: ${SEED}"
  echo "checkpoint_num: ${CHECKPOINT_NUM}"
  echo "gpu_id: ${GPU_ID}"
  echo "instruction_type: ${INSTRUCTION_TYPE}"
  echo "tasks: ${TASKS}"
} | tee "${LOG_ROOT}/run_env.txt"

for task_name in "${TASK_LIST[@]}"; do
  ckpt_file="${ROBOTWIN_ARTIFACT_ROOT}/checkpoints/${task_name}-${CKPT_SETTING}-${EXPERT_DATA_NUM}-${SEED}/${CHECKPOINT_NUM}.ckpt"
  require_file "${ckpt_file}"

  echo
  echo "========== Phase 5 official eval: ${task_name} =========="
  eval_log="${LOG_ROOT}/${task_name}_official_eval.log"
  (
    cd "${ROBOTWIN_ROOT}"
    CUDA_VISIBLE_DEVICES="${GPU_ID}" HYDRA_FULL_ERROR=1 \
      python script/eval_policy.py \
        --config policy/DP/deploy_policy.yml \
        --overrides \
        --task_name "${task_name}" \
        --task_config "${TASK_CONFIG}" \
        --ckpt_setting "${CKPT_SETTING}" \
        --expert_data_num "${EXPERT_DATA_NUM}" \
        --seed "${SEED}" \
        --checkpoint_num "${CHECKPOINT_NUM}" \
        --instruction_type "${INSTRUCTION_TYPE}"
  ) 2>&1 | tee "${eval_log}"

  echo
  echo "========== Phase 5 custom single rollout: ${task_name} =========="
  rollout_log="${LOG_ROOT}/${task_name}_single_rollout.log"
  (
    cd "${PROJECT_ROOT}"
    CUDA_VISIBLE_DEVICES="${GPU_ID}" \
      python scripts/robotwin/single_rollout_demo.py \
        --tasks "${task_name}" \
        --task-config "${TASK_CONFIG}" \
        --ckpt-setting "${CKPT_SETTING}" \
        --expert-data-num "${EXPERT_DATA_NUM}" \
        --seed "${SEED}" \
        --checkpoint-num "${CHECKPOINT_NUM}" \
        --instruction-type "${INSTRUCTION_TYPE}" \
        --output-root "${ROLLOUT_ROOT}"
  ) 2>&1 | tee "${rollout_log}"
done

echo
echo "[done] Phase 5 eval and rollout export finished. Logs: ${LOG_ROOT}"
