#!/bin/bash

# Start Frontend Script

echo "======================================"
echo "Pathfinding Visualization - Frontend"
echo "======================================"
echo ""

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "Starting React development server..."
echo "Application will open at: http://localhost:3000"
echo "Make sure the backend is running on http://localhost:5004"
echo "Press Ctrl+C to stop"
echo ""

cd frontend
npm start

