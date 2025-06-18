#!/bin/bash

# Mojila Signal - Multi-Service Startup Script
# This script runs both the scheduler and web application in parallel

set -e  # Exit on any error

echo "🚀 Starting Mojila Signal Services..."
echo "===================================="

# Function to handle cleanup on exit
cleanup() {
    echo "\n🛑 Shutting down services..."
    # Kill all background jobs
    jobs -p | xargs -r kill
    wait
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Create log directory
mkdir -p logs

# Start the scheduler in the background
echo "📊 Starting Signal Scheduler..."
python scheduler.py > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "   Scheduler PID: $SCHEDULER_PID"

# Wait a moment for scheduler to initialize
sleep 2

# Start the web application in the background
echo "🌐 Starting Web Application..."
python app.py > logs/webapp.log 2>&1 &
WEBAPP_PID=$!
echo "   Web App PID: $WEBAPP_PID"

# Wait a moment for web app to initialize
sleep 3

echo ""
echo "✅ All services started successfully!"
echo "===================================="
echo "📊 Scheduler: Running (PID: $SCHEDULER_PID)"
echo "🌐 Web App: http://localhost:5000 (PID: $WEBAPP_PID)"
echo "📝 Logs: logs/scheduler.log, logs/webapp.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Monitor both processes
while true; do
    # Check if scheduler is still running
    if ! kill -0 $SCHEDULER_PID 2>/dev/null; then
        echo "❌ Scheduler process died, restarting..."
        python scheduler.py > logs/scheduler.log 2>&1 &
        SCHEDULER_PID=$!
        echo "   New Scheduler PID: $SCHEDULER_PID"
    fi
    
    # Check if web app is still running
    if ! kill -0 $WEBAPP_PID 2>/dev/null; then
        echo "❌ Web app process died, restarting..."
        python app.py > logs/webapp.log 2>&1 &
        WEBAPP_PID=$!
        echo "   New Web App PID: $WEBAPP_PID"
    fi
    
    # Wait before next check
    sleep 30
done