#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   APP_DIR=/opt/herbapi DOMAIN_OR_IP=your.host bash deploy/deploy_django.sh
#
# This script:
# - prepares venv
# - installs dependencies
# - runs migrations
# - installs systemd service for gunicorn
# - installs nginx site config

APP_DIR="${APP_DIR:-/opt/herbapi}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$APP_DIR/.venv}"
SERVICE_NAME="${SERVICE_NAME:-herb-django}"
NGINX_SITE_NAME="${NGINX_SITE_NAME:-herbapi}"
DOMAIN_OR_IP="${DOMAIN_OR_IP:-_}"

echo "[Django] App dir: $APP_DIR"

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

python manage.py migrate
python manage.py collectstatic --noinput

sudo cp "deploy/$SERVICE_NAME.service" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager

tmp_nginx_conf="/tmp/${NGINX_SITE_NAME}.conf"
sed "s/__SERVER_NAME__/${DOMAIN_OR_IP}/g; s#__APP_DIR__#${APP_DIR}#g" "deploy/nginx-herbapi.conf" > "$tmp_nginx_conf"
sudo cp "$tmp_nginx_conf" "/etc/nginx/sites-available/${NGINX_SITE_NAME}"
sudo ln -sf "/etc/nginx/sites-available/${NGINX_SITE_NAME}" "/etc/nginx/sites-enabled/${NGINX_SITE_NAME}"
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager

echo "[Django] Deployment completed."
