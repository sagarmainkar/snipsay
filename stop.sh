#!/bin/bash
echo "quit" | nc -U /tmp/whisper_hotkey.sock -w 1 2>/dev/null
echo "Backend stopped."
