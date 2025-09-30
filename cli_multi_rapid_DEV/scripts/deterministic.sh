#!/usr/bin/env bash
set -euo pipefail

# Deterministic Execution Wrapper
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)_$$}"
LOG_DIR=".ai/logs/${RUN_ID}"
STATE_FILE=".ai/state.json"
LOCK_FILE=".ai/pipeline.lock"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
  mkdir -p "${LOG_DIR}"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_DIR}/execution.log"
}

error() {
  echo -e "${RED}[ERROR]${NC} $*" | tee -a "${LOG_DIR}/execution.log" >&2
}

success() {
  echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "${LOG_DIR}/execution.log"
}

write_state() {
  local status="$1"; shift
  local duration="$1"; shift
  local exit_code="${1:-}"
  mkdir -p ".ai"
  if command -v jq >/dev/null 2>&1; then
    if [ -n "$exit_code" ]; then
      jq -n \
        --arg run_id "${RUN_ID}" \
        --arg status "${status}" \
        --arg duration "${duration}" \
        --arg exit_code "${exit_code}" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{run_id:$run_id,status:$status,duration_seconds:($duration|tonumber),exit_code:($exit_code|tonumber),completed_at:$timestamp}' \
        > "${STATE_FILE}"
    else
      jq -n \
        --arg run_id "${RUN_ID}" \
        --arg status "${status}" \
        --arg duration "${duration}" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{run_id:$run_id,status:$status,duration_seconds:($duration|tonumber),completed_at:$timestamp}' \
        > "${STATE_FILE}"
    fi
  else
    python - "$status" "$duration" "$exit_code" "$RUN_ID" "$STATE_FILE" <<'PY'
import json,sys,datetime
status,duration,exit_code,run_id,out = sys.argv[1:6]
obj={
  "run_id": run_id,
  "status": status,
  "duration_seconds": int(duration),
  "completed_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
}
if exit_code:
  try: obj["exit_code"]=int(exit_code)
  except: obj["exit_code"]=exit_code
with open(out,'w') as f:
  json.dump(obj,f,indent=2)
print("state written to", out)
PY
  fi
}

cleanup() {
  rm -rf "${LOCK_FILE}" || true
  log "Released lock"
}

mkdir -p "${LOG_DIR}"

if ! mkdir "${LOCK_FILE}" 2>/dev/null; then
  error "Another pipeline instance is running. Lock exists: ${LOCK_FILE}"
  exit 1
fi

trap cleanup EXIT INT TERM

log "Starting deterministic execution: RUN_ID=${RUN_ID}"
log "Command: $*"

START_TIME=$(date +%s)
set +e
"$@" 2>&1 | tee -a "${LOG_DIR}/command_output.log"
EXIT_CODE=${PIPESTATUS[0]}
set -e
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ "$EXIT_CODE" -eq 0 ]; then
  success "Command completed successfully in ${DURATION}s"
  write_state success "$DURATION"
  exit 0
else
  error "Command failed with exit code ${EXIT_CODE} after ${DURATION}s"
  write_state failed "$DURATION" "$EXIT_CODE"
  exit "$EXIT_CODE"
fi

