#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(pwd)}"
BACKEND_ENV_FILE="${BACKEND_ENV_FILE:-/etc/patient-hospital/backend.env}"
FRONTEND_ENV_FILE="${FRONTEND_ENV_FILE:-/etc/patient-hospital/frontend.env}"
NODE_MAJOR="${NODE_MAJOR:-20}"

if [[ ! -d "$APP_DIR/backend" || ! -d "$APP_DIR/frontend" ]]; then
  echo "Expected to run from repo root or set APP_DIR to repo root." >&2
  exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

echo "Installing system dependencies..."
$SUDO apt-get update -y
$SUDO apt-get install -y \
  curl \
  git \
  build-essential \
  python3 \
  python3-venv \
  python3-pip

if ! command -v node >/dev/null 2>&1; then
  echo "Installing Node.js ${NODE_MAJOR}.x..."
  curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | $SUDO -E bash -
  $SUDO apt-get install -y nodejs
fi

echo "Setting up backend venv..."
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -U pip
"$APP_DIR/.venv/bin/pip" install -e "$APP_DIR/backend"

echo "Creating env files (if missing)..."
$SUDO mkdir -p /etc/patient-hospital
if [[ ! -f "$BACKEND_ENV_FILE" ]]; then
  $SUDO tee "$BACKEND_ENV_FILE" >/dev/null <<'EOF'
OPENAI_API_KEY=
OPENAI_MODEL_TEXT=gpt-4.1-mini
OPENAI_MODEL_REASONING=
OPENAI_MODEL_TTS=gpt-4o-mini-tts
OPENAI_MODEL_STT=whisper-1
DATABASE_URL=sqlite+aiosqlite:///./app.db
REDIS_URL=
MCP_HOSPITAL_BASE_URL=http://localhost:9001
UPLOAD_DIR=./data/uploads
NVIDIA_NIM_API_KEY=
NVIDIA_NIM_PAGE_ELEMENTS_URL=https://ai.api.nvidia.com/v1/cv/nvidia/nemoretriever-page-elements-v3
EOF
  $SUDO chmod 600 "$BACKEND_ENV_FILE"
fi

if [[ ! -f "$FRONTEND_ENV_FILE" ]]; then
  $SUDO tee "$FRONTEND_ENV_FILE" >/dev/null <<'EOF'
NEXT_PUBLIC_API_BASE=http://localhost:8000
PORT=3000
EOF
  $SUDO chmod 600 "$FRONTEND_ENV_FILE"
fi

echo "Installing frontend dependencies..."
cd "$APP_DIR/frontend"
npm ci

echo "Building frontend..."
set -a
source "$FRONTEND_ENV_FILE"
set +a
npm run build

echo "Creating systemd services..."
$SUDO tee /etc/systemd/system/patient-hospital-backend.service >/dev/null <<EOF
[Unit]
Description=Patient & Hospital Backend API
After=network.target

[Service]
WorkingDirectory=$APP_DIR
EnvironmentFile=$BACKEND_ENV_FILE
ExecStart=$APP_DIR/.venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

$SUDO tee /etc/systemd/system/patient-hospital-frontend.service >/dev/null <<EOF
[Unit]
Description=Patient & Hospital Frontend
After=network.target

[Service]
WorkingDirectory=$APP_DIR/frontend
EnvironmentFile=$FRONTEND_ENV_FILE
ExecStart=/usr/bin/npm start
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling services..."
$SUDO systemctl daemon-reload
$SUDO systemctl enable --now patient-hospital-backend.service
$SUDO systemctl enable --now patient-hospital-frontend.service

echo "Done."
echo "Backend: http://<server-ip>:8000"
echo "Frontend: http://<server-ip>:3000"
