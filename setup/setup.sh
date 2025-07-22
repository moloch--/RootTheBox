#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of setup directory)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root directory
cd "$PROJECT_ROOT"

echo "[*] Installing dependencies..."
sudo "$SCRIPT_DIR/depends.sh"

echo "[*] Creating virtual environment..."
python3 -m venv .venv

echo "[*] Activating virtual environment..."
source .venv/bin/activate

echo "[*] Installing python dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt" --upgrade

echo "[*] Python dependencies installed."

echo "[*] Running default sqlite setup... (change later if desired)"
python3 ./rootthebox.py --setup=dev

echo "[*] Setup complete."
echo "[*] Run 'python3 ./rootthebox.py --start' to start the server."