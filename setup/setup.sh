#!/bin/bash

sudo ./depends.sh

echo "[*] Creating virtual environment..."
python3 -m venv .venv

echo "[*] Activating virtual environment..."
source .venv/bin/activate

echo "[*] Installing python dependencies..."
pip3 install -r ./requirements.txt --upgrade

echo "[*] Python dependencies installed."