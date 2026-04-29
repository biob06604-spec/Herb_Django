#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   APP_DIR=/opt/herb_mcp bash deploy/deploy_mcp.sh

APP_DIR="${APP_DIR:-/opt/herb_mcp}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$APP_DIR/.venv}"
SERVICE_NAME="${SERVICE_NAME:-herb-mcp}"

echo "[MCP] App dir: $APP_DIR"

cd "$APP_DIR"

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "ERROR: .env not found in $APP_DIR"
  exit 1
fi

sudo cp "deploy/$SERVICE_NAME.service" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "[MCP] Deployment completed."
