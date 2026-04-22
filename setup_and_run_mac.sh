#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/backend/.env"

read_env_value() {
  local key="$1"
  awk -F= -v key="$key" '$1 == key {print substr($0, index($0, "=") + 1)}' "$ENV_FILE" 2>/dev/null | tail -n 1
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BKMS Bot — One-Command Mac Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$SCRIPT_DIR"
chmod +x install_dependencies.sh setup_mac.sh local_bot.sh

if ! command -v ngrok >/dev/null 2>&1; then
  echo ""
  echo "ngrok is not installed."
  if command -v brew >/dev/null 2>&1; then
    echo "Installing ngrok with Homebrew..."
    brew install ngrok/ngrok/ngrok
  else
    echo "Homebrew is not installed, so ngrok could not be installed automatically."
    echo "Install Homebrew first, then rerun this script."
    exit 1
  fi
fi

echo ""
echo "[1/4] Installing project dependencies..."
bash install_dependencies.sh

if ! ngrok config check >/dev/null 2>&1; then
  echo ""
  echo "[2/4] ngrok authentication is required."
  read -rsp "Enter your ngrok authtoken: " NGROK_AUTH_TOKEN
  echo ""

  if [[ -z "$NGROK_AUTH_TOKEN" ]]; then
    echo "Authtoken cannot be empty."
    exit 1
  fi

  ngrok config add-authtoken "$NGROK_AUTH_TOKEN"
fi

PUBLIC_BASE_URL="$(read_env_value "PUBLIC_BASE_URL")"
BOT_TRIGGER_TOKEN="$(read_env_value "BOT_TRIGGER_TOKEN")"

if [[ -z "$PUBLIC_BASE_URL" || -z "$BOT_TRIGGER_TOKEN" ]]; then
  echo ""
  echo "[3/4] Running one-time local configuration..."
  bash setup_mac.sh
else
  echo ""
  echo "[3/4] Reusing existing local configuration."
  echo "Public URL: $PUBLIC_BASE_URL"
fi

echo ""
echo "[4/4] Starting backend and ngrok..."
bash local_bot.sh

echo ""
echo "All set."
echo "The startup flow now safely syncs from origin/master when the repo is clean."
echo "Use this same command anytime you want to bring everything up:"
echo "  bash setup_and_run_mac.sh"
