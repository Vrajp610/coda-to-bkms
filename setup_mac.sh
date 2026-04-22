#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# BKMS Bot — one-time Mac setup for free Coda button triggering
# This keeps the backend on the user's Mac, exposes it with ngrok,
# and opens Chrome locally when Coda triggers the API.
# ─────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_DIR="$SCRIPT_DIR/launchd"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs"
BACKEND_ENV="$SCRIPT_DIR/backend/.env"
PORT="8000"

mkdir -p "$LAUNCH_AGENTS" "$LOG_DIR"

find_python() {
  if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    echo "$SCRIPT_DIR/.venv/bin/python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi
  echo ""
}

find_ngrok() {
  if command -v ngrok >/dev/null 2>&1; then
    command -v ngrok
    return
  fi
  if [[ -x "/opt/homebrew/bin/ngrok" ]]; then
    echo "/opt/homebrew/bin/ngrok"
    return
  fi
  if [[ -x "/usr/local/bin/ngrok" ]]; then
    echo "/usr/local/bin/ngrok"
    return
  fi
  echo ""
}

upsert_env_var() {
  local key="$1"
  local value="$2"
  local tmp_file

  tmp_file="$(mktemp)"

  mkdir -p "$(dirname "$BACKEND_ENV")"
  touch "$BACKEND_ENV"

  if grep -q "^${key}=" "$BACKEND_ENV"; then
    awk -v key="$key" -v value="$value" '
      BEGIN { updated = 0 }
      $0 ~ ("^" key "=") {
        print key "=" value
        updated = 1
        next
      }
      { print }
      END {
        if (!updated) {
          print key "=" value
        }
      }
    ' "$BACKEND_ENV" > "$tmp_file"
    mv "$tmp_file" "$BACKEND_ENV"
  else
    printf "\n%s=%s\n" "$key" "$value" >> "$BACKEND_ENV"
  fi
}

render_template() {
  local src="$1"
  local dest="$2"
  sed \
    -e "s|__PYTHON__|$PYTHON_BIN|g" \
    -e "s|__WORKDIR__|$SCRIPT_DIR|g" \
    -e "s|__LOGDIR__|$LOG_DIR|g" \
    -e "s|__NGROK__|$NGROK_BIN|g" \
    -e "s|__PORT__|$PORT|g" \
    -e "s|__STATIC_DOMAIN__|$STATIC_DOMAIN|g" \
    "$src" > "$dest"
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BKMS Bot — Mac Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PYTHON_BIN="$(find_python)"
if [[ -z "$PYTHON_BIN" ]]; then
  echo ""
  echo "Python was not found."
  echo "Run ./install_dependencies.sh first, or install Python 3 manually."
  exit 1
fi

NGROK_BIN="$(find_ngrok)"
if [[ -z "$NGROK_BIN" ]]; then
  echo ""
  echo "ngrok was not found."
  echo "Install it first with Homebrew:"
  echo "  brew install ngrok/ngrok/ngrok"
  exit 1
fi

echo ""
echo "Step 1: Checking Python packages..."
if ! "$PYTHON_BIN" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "  Backend dependencies are missing."
  echo "  Run ./install_dependencies.sh first, then re-run this setup."
  exit 1
fi
echo "  ✓ Python and backend packages found"

echo ""
echo "Step 2: Checking ngrok authentication..."
if ! "$NGROK_BIN" config check >/dev/null 2>&1; then
  echo ""
  echo "  ngrok is not authenticated."
  echo "  Run:"
  echo "    ngrok config add-authtoken YOUR_TOKEN"
  echo "  Get your token at: https://dashboard.ngrok.com/get-started/your-authtoken"
  exit 1
fi
echo "  ✓ ngrok auth token found"

echo ""
echo "Step 3: Enter your free ngrok static domain."
echo "  Get one at: https://dashboard.ngrok.com/domains"
echo "  Example: agitative-continuatively-rea.ngrok-free.dev"
read -rp "  Static domain: " STATIC_DOMAIN

if [[ -z "$STATIC_DOMAIN" ]]; then
  echo "  Error: domain cannot be empty."
  exit 1
fi

echo ""
echo "Step 4: Create a trigger token for Coda."
echo "  This protects your public endpoint from random internet traffic."
read -rsp "  Trigger token: " BOT_TRIGGER_TOKEN
echo ""

if [[ -z "$BOT_TRIGGER_TOKEN" ]]; then
  echo "  Error: trigger token cannot be empty."
  exit 1
fi

upsert_env_var "BOT_TRIGGER_TOKEN" "$BOT_TRIGGER_TOKEN"
upsert_env_var "PUBLIC_BASE_URL" "https://${STATIC_DOMAIN}"
echo "  ✓ Saved BOT_TRIGGER_TOKEN in backend/.env"

echo ""
echo "Step 5: Installing LaunchAgents..."
render_template "$PLIST_DIR/com.bkmsbot.backend.plist" "$LAUNCH_AGENTS/com.bkmsbot.backend.plist"
render_template "$PLIST_DIR/com.bkmsbot.ngrok.plist" "$LAUNCH_AGENTS/com.bkmsbot.ngrok.plist"

launchctl unload "$LAUNCH_AGENTS/com.bkmsbot.backend.plist" >/dev/null 2>&1 || true
launchctl unload "$LAUNCH_AGENTS/com.bkmsbot.ngrok.plist" >/dev/null 2>&1 || true

launchctl load "$LAUNCH_AGENTS/com.bkmsbot.backend.plist"
launchctl load "$LAUNCH_AGENTS/com.bkmsbot.ngrok.plist"

echo "  ✓ Backend and ngrok now auto-start on login"

echo ""
echo "Step 6: Health check"
sleep 3
if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
  echo "  ✓ Local backend is responding on http://127.0.0.1:${PORT}/health"
else
  echo "  Warning: backend health check did not respond yet."
  echo "  Check logs:"
  echo "    tail -f \"$LOG_DIR/bkmsbot-backend.log\""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Setup complete!"
echo ""
echo "  Public endpoint:"
echo "    https://${STATIC_DOMAIN}"
echo ""
echo "  Pack settings:"
echo "    Endpoint URL: https://${STATIC_DOMAIN}"
echo "    Token: ${BOT_TRIGGER_TOKEN}"
echo ""
echo "  Important:"
echo "    • This Mac must be on and logged in."
echo "    • Chrome opens on this Mac, not on the caller's device."
echo "    • The user solving CAPTCHA must have access to this Mac."
echo ""
echo "  Useful logs:"
echo "    tail -f \"$LOG_DIR/bkmsbot-backend.log\""
echo "    tail -f \"$LOG_DIR/bkmsbot-ngrok.log\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
