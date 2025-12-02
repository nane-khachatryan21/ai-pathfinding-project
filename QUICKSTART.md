# Quick Start Guide

Get up and running with the Pathfinding Visualization in 3 simple steps!

## Option 1: Using Helper Scripts (Recommended)

### Step 1: Prepare Graph Data (One-time setup)
```bash
cd "AI Final Project/ai-pathfinding-project"
python src/prepare_graphs.py
```
⏱️ This takes 10-30 minutes. Get a coffee! ☕

### Step 2: Start Backend
```bash
./start_backend.sh
```
or
```bash
cd src/api
python server.py
```

### Step 3: Start Frontend (in a new terminal)
```bash
./start_frontend.sh
```
or
```bash
cd frontend
npm install  # first time only
npm start
```

The application will open in your browser at `http://localhost:3000`! 🎉

## Option 2: Manual Setup

### Backend
```bash
# Install dependencies
pip install -r src/api/requirements.txt

# Prepare graphs (one-time, 10-30 minutes)
python src/prepare_graphs.py

# Start server
cd src/api
python server.py
```

### Frontend (New Terminal)
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

## First Time Usage

1. **Select a Graph**: Start with "Armenia Cities" (smallest, fastest)
2. **Choose Algorithm**: Try "A* Search" first
3. **Select Heuristic**: Choose "Euclidean Distance"
4. **Pick Nodes**: Click two cities on the map
5. **Start Search**: Click the "Start Search" button
6. **Watch Magic**: See the algorithm find the path! ✨

## Troubleshooting

### "Graph not found" error
- Run: `python src/prepare_graphs.py`

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r src/api/requirements.txt`

### Frontend won't start
- Check Node version: `node --version` (need 14+)
- Fix npm permissions: `sudo chown -R $(whoami) ~/.npm`
- Reinstall: `cd frontend && rm -rf node_modules && npm install`

### Map not showing
- Ensure backend is running on port 5000
- Check browser console for errors (F12)
- Clear browser cache

## Tips for Best Experience

- **Start Small**: Use "Armenia Cities" graph first (50 nodes)
- **Compare Algorithms**: Run A* vs UCS on the same start/goal
- **Adjust Speed**: Use the speed slider for better visualization
- **Step Through**: Use step forward/backward to understand the algorithm
- **Try Different Graphs**: Each graph offers different complexity levels

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [TESTING.md](TESTING.md) for comprehensive testing guide
- Explore different algorithms and heuristics
- Try adding your own algorithms!

---

**Need Help?** Check the main README.md or open an issue.

**Enjoy the visualization!** 🚀🗺️

