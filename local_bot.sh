#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/backend/.env"
PID_DIR="$SCRIPT_DIR/.run"
LOG_DIR="$SCRIPT_DIR/logs/local"
PORT="8000"

mkdir -p "$PID_DIR" "$LOG_DIR"

read_env_value() {
  local key="$1"
  awk -F= -v key="$key" '$1 == key {print substr($0, index($0, "=") + 1)}' "$ENV_FILE" 2>/dev/null | tail -n 1
}

PUBLIC_BASE_URL="$(read_env_value "PUBLIC_BASE_URL")"
BOT_TRIGGER_TOKEN="$(read_env_value "BOT_TRIGGER_TOKEN")"
PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"

ensure_config() {
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "Missing $ENV_FILE"
    exit 1
  fi
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Missing virtualenv python at $PYTHON_BIN"
    echo "Run: bash install_dependencies.sh"
    exit 1
  fi
  if ! command -v ngrok >/dev/null 2>&1; then
    echo "ngrok is not installed or not on PATH"
    exit 1
  fi
  if [[ -z "$PUBLIC_BASE_URL" ]]; then
    echo "PUBLIC_BASE_URL is not set in backend/.env"
    exit 1
  fi
}

pid_is_running() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] || return 1
  local pid
  pid="$(cat "$pid_file")"
  kill -0 "$pid" >/dev/null 2>&1
}

port_pid() {
  lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | head -n 1
}

sync_repo_from_master() {
  if ! command -v git >/dev/null 2>&1; then
    echo "git is not installed; skipping repo sync"
    return
  fi

  if ! git -C "$SCRIPT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return
  fi

  if ! git -C "$SCRIPT_DIR" remote get-url origin >/dev/null 2>&1; then
    echo "No git origin remote found; skipping repo sync"
    return
  fi

  if [[ -n "$(git -C "$SCRIPT_DIR" status --porcelain)" ]]; then
    echo "Local git changes detected; skipping git pull from origin/main"
    return
  fi

  echo "Syncing latest code from origin/main..."
  if git -C "$SCRIPT_DIR" pull --ff-only origin main; then
    echo "Git sync complete"
  else
    echo "git pull failed; continuing with existing local code"
  fi
}

stop_one() {
  local name="$1"
  local pid_file="$PID_DIR/$name.pid"

  if pid_is_running "$pid_file"; then
    local pid
    pid="$(cat "$pid_file")"
    kill "$pid"
    echo "Stopped $name (pid $pid)"
  else
    echo "$name is not running"
  fi

  rm -f "$pid_file"
}

stop_matching_ngrok_processes() {
  local ngrok_url="${PUBLIC_BASE_URL#https://}"
  local pids

  pids="$(pgrep -f "ngrok http --url=${ngrok_url} ${PORT}" || true)"
  if [[ -n "$pids" ]]; then
    echo "$pids" | while read -r pid; do
      [[ -n "$pid" ]] || continue
      kill "$pid" >/dev/null 2>&1 || true
      echo "Stopped stale ngrok process (pid $pid)"
    done
  fi
}

start_backend() {
  local pid_file="$PID_DIR/backend.pid"

  if pid_is_running "$pid_file"; then
    echo "backend is already running (pid $(cat "$pid_file"))"
    return
  fi

  local existing_pid
  existing_pid="$(port_pid || true)"
  if [[ -n "$existing_pid" ]]; then
    echo "Stopping process already using port $PORT (pid $existing_pid)"
    kill "$existing_pid" >/dev/null 2>&1 || true
    sleep 1
  fi

  echo "Starting backend on http://127.0.0.1:${PORT}"
  nohup "$PYTHON_BIN" -m uvicorn backend.index:app --host 127.0.0.1 --port "$PORT" \
    > "$LOG_DIR/backend.log" 2>&1 &
  echo "$!" > "$pid_file"

  for _ in {1..20}; do
    if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
      return
    fi
    sleep 1
  done

  echo "Backend failed to start. Check $LOG_DIR/backend.log"
  exit 1
}

start_ngrok() {
  local pid_file="$PID_DIR/ngrok.pid"
  local ngrok_url="${PUBLIC_BASE_URL#https://}"

  if pid_is_running "$pid_file"; then
    echo "ngrok is already running (pid $(cat "$pid_file"))"
    return
  fi

  stop_matching_ngrok_processes

  echo "Starting ngrok on $PUBLIC_BASE_URL"
  nohup ngrok http --url="$ngrok_url" "$PORT" \
    > "$LOG_DIR/ngrok.log" 2>&1 &
  echo "$!" > "$pid_file"
  sleep 3

  if ! pid_is_running "$pid_file"; then
    echo "ngrok failed to start. Check $LOG_DIR/ngrok.log"
    exit 1
  fi
}

show_status() {
  echo "BKMS Bot status"
  echo "---------------"

  if pid_is_running "$PID_DIR/backend.pid"; then
    echo "backend: running (pid $(cat "$PID_DIR/backend.pid"))"
  else
    echo "backend: stopped"
  fi

  if pid_is_running "$PID_DIR/ngrok.pid"; then
    echo "ngrok: running (pid $(cat "$PID_DIR/ngrok.pid"))"
  else
    echo "ngrok: stopped"
  fi

  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "local health: ok"
  else
    echo "local health: down"
  fi

  if [[ -n "$PUBLIC_BASE_URL" ]]; then
    echo "public url: $PUBLIC_BASE_URL"
  fi

  if [[ -n "$BOT_TRIGGER_TOKEN" ]]; then
    echo "token header: X-Bkms-Token: $BOT_TRIGGER_TOKEN"
  fi
}

call_health() {
  ensure_config
  local target_url
  local label

  if [[ "${1:-}" == "local" ]]; then
    target_url="http://127.0.0.1:${PORT}/health"
    label="local"
  else
    target_url="${PUBLIC_BASE_URL}/health"
    label="public"
  fi

  echo "Checking ${label} health: $target_url"
  if [[ -n "$BOT_TRIGGER_TOKEN" && "$label" == "public" ]]; then
    curl -fsS -H "X-Bkms-Token: $BOT_TRIGGER_TOKEN" "$target_url"
  else
    curl -fsS "$target_url"
  fi
  echo ""
}

run_test_bot() {
  ensure_config
  local date="${2:-2026-04-12}"
  local group="${3:-Sunday K1}"
  local sabha_held="${4:-Yes}"
  local p2_guju="${5:-No}"
  local prep_cycle_done="${6:-Yes}"

  echo "Triggering test run against ${PUBLIC_BASE_URL}/run-bot"
  curl -fsS \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Bkms-Token: $BOT_TRIGGER_TOKEN" \
    "${PUBLIC_BASE_URL}/run-bot" \
    -d "{\"date\":\"${date}\",\"group\":\"${group}\",\"sabhaHeld\":\"${sabha_held}\",\"p2Guju\":\"${p2_guju}\",\"prepCycleDone\":\"${prep_cycle_done}\"}"
  echo ""
}

start_all() {
  ensure_config
  sync_repo_from_master
  stop_one "ngrok" >/dev/null 2>&1 || true
  stop_one "backend" >/dev/null 2>&1 || true
  start_backend
  start_ngrok
  echo ""
  echo "BKMS Bot is running"
  echo "Local health:  http://127.0.0.1:${PORT}/health"
  echo "Public URL:    ${PUBLIC_BASE_URL}"
  echo "Backend log:   $LOG_DIR/backend.log"
  echo "ngrok log:     $LOG_DIR/ngrok.log"
}

stop_all() {
  stop_one "ngrok"
  stop_one "backend"
}

DEFAULT_ACTION="${1:-run}"

case "$DEFAULT_ACTION" in
  run)
    start_all
    echo ""
    show_status
    ;;
  start)
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    stop_all
    start_all
    ;;
  status)
    ensure_config
    show_status
    ;;
  health)
    call_health "public"
    ;;
  health-local)
    call_health "local"
    ;;
  test-run)
    run_test_bot "$@"
    ;;
  *)
    echo "Usage: bash local_bot.sh [start|stop|restart|status|health|health-local|test-run]"
    echo "No argument defaults to: run"
    exit 1
    ;;
esac
