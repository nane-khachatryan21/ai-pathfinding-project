import React from 'react';
import { useSearch } from '../context/SearchContext';

const ControlPanel = () => {
  const {
    graphs,
    algorithms,
    heuristics,
    selectedGraph,
    setSelectedGraph,
    selectedAlgorithm,
    setSelectedAlgorithm,
    selectedHeuristic,
    setSelectedHeuristic,
    startNode,
    setStartNode,
    goalNode,
    setGoalNode,
    isSearching,
    searchCompleted,
    beginSearch,
    resetSearch,
    isPlaying,
    play,
    pause,
    stepForward,
    stepBackward,
    speed,
    setSpeed,
    currentStep,
    searchSteps,
    goToStep,
  } = useSearch();

  const currentAlgo = algorithms.find(a => a.name === selectedAlgorithm);
  const needsHeuristic = currentAlgo?.requires_heuristic || false;
  const canSearch = startNode && goalNode && !isSearching;

  const handleGraphChange = (e) => {
    setSelectedGraph(e.target.value);
  };

  const handleAlgorithmChange = (e) => {
    setSelectedAlgorithm(e.target.value);
  };

  const handleHeuristicChange = (e) => {
    setSelectedHeuristic(e.target.value);
  };

  const handleClearStart = () => {
    setStartNode(null);
  };

  const handleClearGoal = () => {
    setGoalNode(null);
  };

  const handleReset = () => {
    resetSearch();
    setStartNode(null);
    setGoalNode(null);
  };

  const handleSpeedChange = (e) => {
    setSpeed(parseFloat(e.target.value));
  };

  const handleStepSliderChange = (e) => {
    goToStep(parseInt(e.target.value));
  };

  return (
    <div className="control-panel">
      <div className="control-section">
        <h3>Graph Selection</h3>
        <select
          value={selectedGraph || ''}
          onChange={handleGraphChange}
          disabled={isSearching}
          className="control-select"
        >
          {graphs.map(graph => (
            <option key={graph.graph_id} value={graph.graph_id}>
              {graph.name}
            </option>
          ))}
        </select>
      </div>

      <div className="control-section">
        <h3>Algorithm</h3>
        <select
          value={selectedAlgorithm || ''}
          onChange={handleAlgorithmChange}
          disabled={isSearching}
          className="control-select"
        >
          {algorithms.map(algo => (
            <option key={algo.name} value={algo.name}>
              {algo.display_name}
            </option>
          ))}
        </select>
      </div>

      {needsHeuristic && (
        <div className="control-section">
          <h3>Heuristic</h3>
          <select
            value={selectedHeuristic || ''}
            onChange={handleHeuristicChange}
            disabled={isSearching}
            className="control-select"
          >
            {heuristics.map(heur => (
              <option key={heur.name} value={heur.name}>
                {heur.display_name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="control-section">
        <h3>Nodes</h3>
        <div className="node-selection">
          <div className="node-item">
            <span className="node-label">Start:</span>
            <span className="node-value">
              {startNode || 'Click on map'}
            </span>
            {startNode && !isSearching && (
              <button onClick={handleClearStart} className="btn-clear">×</button>
            )}
          </div>
          <div className="node-item">
            <span className="node-label">Goal:</span>
            <span className="node-value">
              {goalNode || 'Click on map'}
            </span>
            {goalNode && !isSearching && (
              <button onClick={handleClearGoal} className="btn-clear">×</button>
            )}
          </div>
        </div>
      </div>

      <div className="control-section">
        <h3>Search Control</h3>
        <button
          onClick={beginSearch}
          disabled={!canSearch}
          className="btn-primary"
        >
          {isSearching ? 'Searching...' : 'Start Search'}
        </button>
        <button
          onClick={handleReset}
          disabled={isSearching}
          className="btn-secondary"
        >
          Reset
        </button>
      </div>

      {searchSteps.length > 0 && (
        <>
          <div className="control-section">
            <h3>Animation</h3>
            <div className="animation-controls">
              <button
                onClick={stepBackward}
                disabled={currentStep === 0}
                className="btn-icon"
                title="Step backward"
              >
                ⏮
              </button>
              <button
                onClick={isPlaying ? pause : play}
                disabled={currentStep >= searchSteps.length - 1 && !isPlaying}
                className="btn-icon"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? '⏸' : '▶'}
              </button>
              <button
                onClick={stepForward}
                disabled={currentStep >= searchSteps.length - 1}
                className="btn-icon"
                title="Step forward"
              >
                ⏭
              </button>
            </div>
          </div>

          <div className="control-section">
            <h3>Speed: {speed}x</h3>
            <input
              type="range"
              min="0.1"
              max="10"
              step="0.1"
              value={speed}
              onChange={handleSpeedChange}
              className="slider"
            />
          </div>

          <div className="control-section">
            <h3>Progress</h3>
            <input
              type="range"
              min="0"
              max={searchSteps.length - 1}
              value={currentStep}
              onChange={handleStepSliderChange}
              className="slider"
            />
            <div className="step-info">
              Step {currentStep + 1} / {searchSteps.length}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ControlPanel;

