#!/bin/bash
set -e

# Detect architecture
ARCH=$(uname -m)
echo "=========================================================="
echo " Starting EcoTrack AI / CleanConnect on Architecture: $ARCH"
echo "=========================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install python3."
    exit 1
fi

# Create virtualenv if not present
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install / update dependencies
echo "Verifying dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
fi

# Start FastAPI application with uvicorn on 0.0.0.0:8000
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Launching EcoTrack AI server on http://$HOST:$PORT ..."
exec uvicorn backend.main:app --host "$HOST" --port "$PORT"
