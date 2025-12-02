#!/bin/bash

# Start Backend Server Script

echo "======================================"
echo "Pathfinding Visualization - Backend"
echo "======================================"
echo ""

# Check if graphs exist
if [ ! -d "src/graphs" ] || [ -z "$(ls -A src/graphs 2>/dev/null)" ]; then
    echo "⚠️  Graph data not found!"
    echo "Please run: python src/prepare_graphs.py"
    echo ""
    read -p "Would you like to prepare graphs now? This will take 10-30 minutes. (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Preparing graphs..."
        cd src
        python prepare_graphs.py
        cd ..
    else
        echo "Exiting. Please prepare graphs before starting the server."
        exit 1
    fi
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r src/api/requirements.txt
fi

echo ""
echo "Starting Flask server..."
echo "Server will be available at: http://localhost:5004"
echo "Press Ctrl+C to stop"
echo ""

cd src/api
python server.py

