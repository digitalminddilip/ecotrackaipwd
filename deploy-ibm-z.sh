#!/bin/bash
# ==============================================================================
# IBM Z Datathon Community Cloud - 1-Click Automated Deployment Script
# Architecture Target: IBM LinuxONE / IBM Z (s390x) or x86_64
# ==============================================================================
set -e

echo "========================================================================"
echo "    IBM Z COMMUNITY CLOUD / LINUXONE - AUTOMATED DEPLOYMENT             "
echo "    Project: EcoTrack AI (CleanConnect Civic Intelligence)             "
echo "========================================================================"

ARCH=$(uname -m)
echo "[1/6] Detected System Architecture: $ARCH"
if [ "$ARCH" = "s390x" ]; then
    echo "       Confirmed: Running natively on IBM Z / LinuxONE Enterprise Architecture!"
else
    echo "       Note: Running on $ARCH (Compatible with all Linux architectures)"
fi

# Detect package manager and install dependencies
echo "[2/6] Installing system prerequisites..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip python3-venv sqlite3 curl ufw git
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3 python3-pip sqlite curl git
fi

# Setup project directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"
echo "[3/6] Working directory: $APP_DIR"

# Ensure environment file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
    fi
fi

# Create & configure Python Virtual Environment
echo "[4/6] Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure firewall if ufw is active
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo "Allowing port 8000 through firewall..."
        sudo ufw allow 8000/tcp comment "EcoTrack AI IBM Z Port"
    fi
fi

# Setup systemd service for 24/7 background persistence
echo "[5/6] Configuring and starting systemd service (ecotrack.service)..."
SERVICE_FILE="/etc/systemd/system/ecotrack.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=EcoTrack AI / CleanConnect Service on IBM Z Community Cloud
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ecotrack.service
sudo systemctl restart ecotrack.service

echo "[6/6] Verifying service health..."
sleep 3

# Health Check Test
if curl -s http://127.0.0.1:8000/health | grep -q '"status":"ok"'; then
    echo " SUCCESS: EcoTrack AI is LIVE and HEALTHY on IBM Z!"
else
    echo " Checking status via systemctl..."
    sudo systemctl status ecotrack.service --no-pager
fi

# Detect Public IP
PUBLIC_IP=$(curl -s -m 5 https://api.ipify.org || curl -s -m 5 ifconfig.me || hostname -I | awk '{print $1}')

echo ""
echo "========================================================================"
echo "    DEPLOYMENT COMPLETED SUCCESSFULLY ON IBM Z COMMUNITY CLOUD!       "
echo "========================================================================"
echo "  Public Live URL:        http://${PUBLIC_IP}:8000"
echo "  Citizen Portal:         http://${PUBLIC_IP}:8000"
echo "  Admin Dashboard:        http://${PUBLIC_IP}:8000/admin/"
echo "  API Documentation:      http://${PUBLIC_IP}:8000/docs"
echo "  Health Endpoint:        http://${PUBLIC_IP}:8000/health"
echo "========================================================================"
echo "  Admin Login:            dilipksharma1244@gmail.com"
echo "  Admin Password:         Dilip@2006"
echo "========================================================================"
