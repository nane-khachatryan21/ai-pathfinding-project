# Testing Guide

This document provides comprehensive testing instructions for the Pathfinding Visualization project.

## Prerequisites

Before testing, ensure:
1. Backend is running (`python src/api/server.py`)
2. Frontend is running (`npm start` in frontend directory)
3. Graph data has been prepared (`python src/prepare_graphs.py`)

## Manual Testing Checklist

### 1. Backend API Testing

#### Test Health Endpoint
```bash
curl http://localhost:5004/api/health
```
Expected: JSON response with `success: true` and counts of available graphs/algorithms

#### Test Graphs Endpoint
```bash
curl http://localhost:5004/api/graphs
```
Expected: List of 3 graphs (Armenia Cities, Armenia Cities & Villages, Yerevan)

#### Test Algorithms Endpoint
```bash
curl http://localhost:5004/api/algorithms
```
Expected: List of 7 algorithms (UCS, A*, Bidirectional, BFS Graph, BFS Tree, DFS Graph, DFS Tree)

#### Test Heuristics Endpoint
```bash
curl http://localhost:5004/api/heuristics
```
Expected: List of heuristics (at minimum: Euclidean/Haversine)

### 2. Frontend UI Testing

#### Initial Load
- [ ] Application loads without errors
- [ ] Dark theme is applied correctly
- [ ] Sidebar displays all controls
- [ ] Map loads with default graph

#### Graph Selection
- [ ] All three graph options appear in dropdown
- [ ] Selecting "Armenia Cities" loads city-level graph
- [ ] Selecting "Armenia Cities & Villages" loads extended graph
- [ ] Selecting "Yerevan" loads Yerevan street network
- [ ] Map bounds adjust correctly when switching graphs
- [ ] Start and goal nodes are cleared when switching graphs

#### Node Selection
- [ ] Clicking on map selects start node (green marker)
- [ ] Clicking again selects goal node (red marker)
- [ ] Node IDs display correctly in control panel
- [ ] Clear buttons (×) remove selected nodes
- [ ] Cannot select same node for both start and goal

#### Algorithm Selection
- [ ] All algorithms appear in algorithm dropdown
- [ ] Selecting A* enables heuristic dropdown
- [ ] Selecting non-heuristic algorithm disables heuristic dropdown
- [ ] Algorithm descriptions display correctly

### 3. Search Algorithm Testing

Test each algorithm with different graph configurations:

#### Test: A* Search on Armenia Cities
1. Select "Armenia Cities" graph
2. Select "A* Search" algorithm
3. Select "Euclidean Distance" heuristic
4. Click two distant cities on map
5. Click "Start Search"
6. Verify:
   - [ ] Search runs without errors
   - [ ] Steps are generated
   - [ ] Frontier nodes (orange) expand outward
   - [ ] Expanded nodes (blue) are marked
   - [ ] Solution path (green) is found
   - [ ] Animation controls work

#### Test: UCS on Yerevan
1. Select "Yerevan" graph
2. Select "Uniform Cost Search" algorithm
3. Click two points in Yerevan
4. Click "Start Search"
5. Verify:
   - [ ] Search completes successfully
   - [ ] No heuristic dropdown appears
   - [ ] Optimal path is found
   - [ ] Stats show nodes expanded and frontier size

#### Test: Bidirectional Search
1. Select any graph
2. Select "Bidirectional Search"
3. Select start and goal nodes
4. Click "Start Search"
5. Verify:
   - [ ] Search runs from both directions
   - [ ] Meeting point is identified
   - [ ] Solution path is correct

#### Test: BFS vs DFS
1. Select "Armenia Cities" graph
2. Run BFS Graph Search
3. Note nodes expanded count
4. Reset and run DFS Graph Search with same start/goal
5. Verify:
   - [ ] BFS explores level by level
   - [ ] DFS explores depth first
   - [ ] Both find solutions (if exists)
   - [ ] Expansion patterns differ visually

### 4. Animation Testing

#### Playback Controls
- [ ] Play button starts animation
- [ ] Pause button stops animation
- [ ] Step forward advances one step
- [ ] Step backward goes back one step
- [ ] Progress slider allows jumping to any step

#### Speed Control
- [ ] Speed slider ranges from 0.1x to 10x
- [ ] Animation speed increases with slider
- [ ] Speed changes apply immediately during playback

#### Visual Animation
- [ ] Frontier nodes pulse with animation
- [ ] Expanded nodes appear smoothly
- [ ] Solution path draws with animation
- [ ] No flickering or visual glitches

### 5. Statistics Testing

Verify statistics panel shows:
- [ ] Current graph name, node count, edge count
- [ ] Current step number / total steps
- [ ] Nodes expanded count (increments correctly)
- [ ] Frontier size (updates correctly)
- [ ] Current path cost (for current node)
- [ ] Final path length (nodes in solution)
- [ ] Final path cost (total distance in meters)

### 6. Edge Cases

#### No Solution
1. Select graph with disconnected components (if any)
2. Select nodes in different components
3. Verify:
   - [ ] Search completes
   - [ ] "No Solution Found" message appears
   - [ ] Application doesn't crash

#### Same Start and Goal
1. Click same node for start
2. Try to select same node for goal
3. Verify:
   - [ ] Cannot select same node
   - [ ] Or immediate solution if allowed

#### Very Long Path
1. Select nodes at opposite ends of Armenia
2. Run search
3. Verify:
   - [ ] Search completes (may take time)
   - [ ] Memory usage stays reasonable
   - [ ] Animation is smooth

### 7. Error Handling

#### Backend Down
1. Stop Flask server
2. Try to start search
3. Verify:
   - [ ] Error message appears
   - [ ] Application doesn't crash
   - [ ] Can retry after server restarts

#### Network Interruption
1. Start a long search
2. Simulate network interruption
3. Verify:
   - [ ] Graceful error handling
   - [ ] Can reset and retry

### 8. Browser Compatibility

Test in:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### 9. Responsive Design

Test at different screen sizes:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768px width)
- [ ] Mobile (375px width)

### 10. Performance Testing

#### Large Graph (Yerevan)
- [ ] Graph loads in reasonable time (< 10 seconds)
- [ ] Map renders smoothly
- [ ] Search completes in reasonable time
- [ ] Animation maintains 30+ FPS

#### Many Steps
- [ ] Search with 1000+ steps doesn't cause lag
- [ ] Progress slider works smoothly
- [ ] Memory usage stays under 500MB

## Automated Testing (Future)

### Backend Unit Tests
```python
# Example test structure
def test_ucs_search():
    graph = load_test_graph()
    start = graph.nodes[0]
    goal = graph.nodes[10]
    algo = UCSGraphSearch()
    result = algo.find_solution(GraphState(graph, start), SimpleGoalTest(goal))
    assert result is not None
```

### Frontend Component Tests
```javascript
// Example test structure
test('MapView renders correctly', () => {
  render(<MapView />);
  expect(screen.getByRole('map')).toBeInTheDocument();
});
```

### Integration Tests
- API endpoint integration
- Full search flow from frontend to backend
- Data consistency checks

## Bug Reporting Template

If you encounter issues during testing:

```
**Issue**: [Brief description]
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**: 
**Actual Behavior**: 
**Browser/Environment**: 
**Screenshots**: [If applicable]
**Console Errors**: [If any]
```

## Testing Results Summary

After completing tests, summarize results:

| Test Category | Pass | Fail | Notes |
|--------------|------|------|-------|
| Backend API | ☐ | ☐ | |
| UI/UX | ☐ | ☐ | |
| Algorithms | ☐ | ☐ | |
| Animation | ☐ | ☐ | |
| Statistics | ☐ | ☐ | |
| Edge Cases | ☐ | ☐ | |
| Performance | ☐ | ☐ | |

---

**Testing completed by**: _______________  
**Date**: _______________  
**Overall Status**: ☐ Pass ☐ Fail ☐ Needs Improvement

