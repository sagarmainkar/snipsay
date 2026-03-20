#!/bin/bash
# Start Whisper Hotkey backend
# Usage: ./start.sh [--model tiny|base|small|medium|large-v3]

cd "$(dirname "$0")"

# Source virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: venv not found. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate

# Check if already running
if pgrep -f "whisper_hotkey.py" > /dev/null; then
    echo "Backend is already running. Run ./stop.sh first."
    exit 1
fi

# Default model
MODEL="base"

# Parse --model argument
if [ "$1" = "--model" ] && [ -n "$2" ]; then
    MODEL="$2"
fi

# Start the backend
echo "Starting Whisper Hotkey with model: $MODEL"
python3 whisper_hotkey.py --model "$MODEL"
