#!/bin/bash

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    echo "Error: Virtual environment not found. Please run setup/depends.sh first."
    echo "Or run: python3 -m venv .venv && pip3 install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Run RootTheBox
python3 rootthebox.py --start