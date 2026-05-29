#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Phase 4: serial RoboTwin Diffusion Policy preprocessing and training.

Run from the course repo after Phase 3:
  pixi run robotwin-phase4-train

Environment overrides:
  TASKS="grab_roller adjust_bottle place_burger_fries"
  TASK_CONFIG=demo_clean_100
  EXPERT_DATA_NUM=100
  SEED=0
  GPU_ID=0
  ROBOTWIN_ARTIFACT_ROOT=outputs/robotwin/artifacts
  TRAIN_EPOCHS=200
  CHECKPOINT_EVERY=200
  BATCH_SIZE=32
  MAX_TRAIN_STEPS=100
  MAX_VAL_STEPS=20
  GRADIENT_ACCUMULATE_EVERY=1
  USE_EMA=False
  REPROCESS_ZARR=0
  NUM_INFERENCE_STEPS=100
  NOISE_TIMESTEPS=100
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
  ROBOTWIN_ROOT=../RoboTwin-Project/RoboTwin
  LOG_ROOT=outputs/robotwin/logs/phase4_<timestamp>

This is a heavy foreground command. Defaults balance course runtime and a
verified 12GB GPU run. If it OOMs, retry with BATCH_SIZE=16, then BATCH_SIZE=8.
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
EXPERT_DATA_NUM="${EXPERT_DATA_NUM:-100}"
SEED="${SEED:-0}"
GPU_ID="${GPU_ID:-0}"
TRAIN_EPOCHS="${TRAIN_EPOCHS:-200}"
CHECKPOINT_EVERY="${CHECKPOINT_EVERY:-200}"
BATCH_SIZE="${BATCH_SIZE:-32}"
MAX_TRAIN_STEPS="${MAX_TRAIN_STEPS:-100}"
MAX_VAL_STEPS="${MAX_VAL_STEPS:-20}"
GRADIENT_ACCUMULATE_EVERY="${GRADIENT_ACCUMULATE_EVERY:-1}"
USE_EMA="${USE_EMA:-False}"
REPROCESS_ZARR="${REPROCESS_ZARR:-0}"
NUM_INFERENCE_STEPS="${NUM_INFERENCE_STEPS:-100}"
NOISE_TIMESTEPS="${NOISE_TIMESTEPS:-100}"
PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_ROOT="${LOG_ROOT:-${PROJECT_ROOT}/outputs/robotwin/logs/phase4_${STAMP}}"
export ROBOTWIN_ROOT ROBOTWIN_ARTIFACT_ROOT PYTORCH_CUDA_ALLOC_CONF

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
require_file "${ROBOTWIN_ROOT}/policy/DP/process_data.py"
require_file "${ROBOTWIN_ROOT}/policy/DP/train.py"
copy_project_config_if_present
if (( TRAIN_EPOCHS % CHECKPOINT_EVERY != 0 )); then
  echo "[error] TRAIN_EPOCHS must be divisible by CHECKPOINT_EVERY so the expected final checkpoint is saved." >&2
  exit 2
fi
mkdir -p "${LOG_ROOT}"
read -r -a TASK_LIST <<< "${TASKS}"
python "${PROJECT_ROOT}/scripts/robotwin/prepare_artifact_links.py" \
  --tasks "${TASK_LIST[@]}" \
  --task-configs "${TASK_CONFIG}" \
  --link-data \
  --link-dp-data \
  --link-checkpoints

{
  echo "phase: 4"
  echo "timestamp: ${STAMP}"
  echo "project_root: ${PROJECT_ROOT}"
  echo "robotwin_root: ${ROBOTWIN_ROOT}"
  echo "artifact_root: ${ROBOTWIN_ARTIFACT_ROOT}"
  echo "task_config: ${TASK_CONFIG}"
  echo "expert_data_num: ${EXPERT_DATA_NUM}"
  echo "seed: ${SEED}"
  echo "gpu_id: ${GPU_ID}"
  echo "train_epochs: ${TRAIN_EPOCHS}"
  echo "checkpoint_every: ${CHECKPOINT_EVERY}"
  echo "batch_size: ${BATCH_SIZE}"
  echo "max_train_steps: ${MAX_TRAIN_STEPS}"
  echo "max_val_steps: ${MAX_VAL_STEPS}"
  echo "gradient_accumulate_every: ${GRADIENT_ACCUMULATE_EVERY}"
  echo "use_ema: ${USE_EMA}"
  echo "reprocess_zarr: ${REPROCESS_ZARR}"
  echo "pytorch_cuda_alloc_conf: ${PYTORCH_CUDA_ALLOC_CONF}"
  echo "tasks: ${TASKS}"
} | tee "${LOG_ROOT}/run_env.txt"

for task_name in "${TASK_LIST[@]}"; do
  echo
  echo "========== Phase 4 DP preprocessing: ${task_name} =========="
  data_dir="${ROBOTWIN_ARTIFACT_ROOT}/data/${task_name}/${TASK_CONFIG}/data"
  require_dir "${data_dir}"
  hdf5_count="$(find "${data_dir}" -maxdepth 1 -name 'episode*.hdf5' | wc -l)"
  if [[ "${hdf5_count}" -lt "${EXPERT_DATA_NUM}" ]]; then
    echo "[error] ${task_name}: expected ${EXPERT_DATA_NUM} HDF5 files, found ${hdf5_count}" >&2
    exit 3
  fi

  process_log="${LOG_ROOT}/${task_name}_process.log"
  zarr_dir="${ROBOTWIN_ARTIFACT_ROOT}/dp_data/${task_name}-${TASK_CONFIG}-${EXPERT_DATA_NUM}.zarr"
  if [[ "${REPROCESS_ZARR}" == "0" && -f "${zarr_dir}/.zgroup" ]]; then
    echo "[skip] ${task_name}: existing zarr ${zarr_dir}" | tee "${process_log}"
  else
    (
      cd "${ROBOTWIN_ROOT}/policy/DP"
      python process_data.py "${task_name}" "${TASK_CONFIG}" "${EXPERT_DATA_NUM}"
    ) 2>&1 | tee "${process_log}"
  fi
  require_file "${zarr_dir}/.zgroup"

  echo
  echo "========== Phase 4 DP training: ${task_name} =========="
  train_log="${LOG_ROOT}/${task_name}_train.log"
  (
    cd "${ROBOTWIN_ROOT}/policy/DP"
    CUDA_VISIBLE_DEVICES="${GPU_ID}" WANDB_MODE=offline HYDRA_FULL_ERROR=1 \
      python train.py \
        --config-name=robot_dp_14.yaml \
        "task.name=${task_name}" \
        "task.dataset.zarr_path=data/${task_name}-${TASK_CONFIG}-${EXPERT_DATA_NUM}.zarr" \
        "training.debug=False" \
        "training.resume=False" \
        "training.seed=${SEED}" \
        "training.device=cuda:0" \
        "training.num_epochs=${TRAIN_EPOCHS}" \
        "training.checkpoint_every=${CHECKPOINT_EVERY}" \
        "training.max_train_steps=${MAX_TRAIN_STEPS}" \
        "training.max_val_steps=${MAX_VAL_STEPS}" \
        "training.gradient_accumulate_every=${GRADIENT_ACCUMULATE_EVERY}" \
        "training.use_ema=${USE_EMA}" \
        "dataloader.batch_size=${BATCH_SIZE}" \
        "val_dataloader.batch_size=${BATCH_SIZE}" \
        "policy.num_inference_steps=${NUM_INFERENCE_STEPS}" \
        "policy.noise_scheduler.num_train_timesteps=${NOISE_TIMESTEPS}" \
        "exp_name=${task_name}-robot_dp-course" \
        "logging.mode=offline" \
        "setting=${TASK_CONFIG}" \
        "expert_data_num=${EXPERT_DATA_NUM}" \
        "head_camera_type=D435" \
        "hydra.run.dir=data/outputs/${task_name}_dp_${TASK_CONFIG}_${EXPERT_DATA_NUM}_seed${SEED}"
  ) 2>&1 | tee "${train_log}"

  ckpt_file="${ROBOTWIN_ARTIFACT_ROOT}/checkpoints/${task_name}-${TASK_CONFIG}-${EXPERT_DATA_NUM}-${SEED}/${TRAIN_EPOCHS}.ckpt"
  require_file "${ckpt_file}"
  echo "[ok] ${task_name}: checkpoint ${ckpt_file}"
done

echo
echo "[done] Phase 4 DP training finished. Logs: ${LOG_ROOT}"
