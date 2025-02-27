#!/bin/sh
set -e

CONFIG_DIR="/tmp/nginx"
mkdir -p $CONFIG_DIR

BACKEND_URL="${BACKEND_URL:-$1}"
FRONTEND_PORT="${FRONTEND_PORT:-${2:-80}}"
VITE_BASENAME="${VITE_BASENAME:-/onlyflow/}"; VITE_BASENAME="${VITE_BASENAME%/}"

if [ -z "$BACKEND_URL" ]; then
  echo "BACKEND_URL must be set as an environment variable or as the first parameter. (e.g., http://localhost:7860)"
  exit 1
fi

export BACKEND_URL FRONTEND_PORT VITE_BASENAME
envsubst '${BACKEND_URL} ${FRONTEND_PORT} ${VITE_BASENAME}' < /etc/nginx/conf.d/default.conf.template > $CONFIG_DIR/default.conf
exec nginx -c $CONFIG_DIR/default.conf -g 'daemon off;'
