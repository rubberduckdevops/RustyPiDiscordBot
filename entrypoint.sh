#!/bin/bash

# Exit on error
set -e

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    kill $API_PID 2>/dev/null || true
    kill $BOT_PID 2>/dev/null || true
    exit 0
}

# Trap SIGTERM and SIGINT
trap shutdown SIGTERM SIGINT

echo "Starting Flask API..."
python api.py &
API_PID=$!

echo "Starting Discord Bot..."
python bot.py &
BOT_PID=$!

echo "Both services started. API PID: $API_PID, Bot PID: $BOT_PID"

# Wait for both processes
wait $API_PID $BOT_PID
