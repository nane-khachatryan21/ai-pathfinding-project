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
    startNodeInput,
    goalNodeInput,
    handleStartNodeInputChange,
    handleGoalNodeInputChange,
    startNodeValidation,
    goalNodeValidation,
    reachabilityCheck,
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
    getAccumulatedData,
  } = useSearch();

  const currentAlgo = algorithms.find(a => a.name === selectedAlgorithm);
  const needsHeuristic = currentAlgo?.requires_heuristic || false;
  const canSearch = startNode && goalNode && !isSearching && 
                    startNodeValidation.status === 'valid' && 
                    goalNodeValidation.status === 'valid' &&
                    reachabilityCheck.status !== 'unreachable';

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
    handleStartNodeInputChange('');
  };

  const handleClearGoal = () => {
    setGoalNode(null);
    handleGoalNodeInputChange('');
  };

  const handleReset = () => {
    resetSearch();
    setStartNode(null);
    setGoalNode(null);
    handleStartNodeInputChange('');
    handleGoalNodeInputChange('');
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
          <div className="node-input-group">
            <label className="node-label">Start Node:</label>
            <div className="input-with-validation">
              <input
                type="text"
                value={startNodeInput}
                onChange={(e) => handleStartNodeInputChange(e.target.value)}
                placeholder="Enter node ID or click on map"
                disabled={isSearching}
                className={`node-input ${startNodeValidation.status === 'valid' ? 'valid' : ''} ${startNodeValidation.status === 'invalid' ? 'invalid' : ''}`}
              />
              {startNode && !isSearching && (
                <button onClick={handleClearStart} className="btn-clear-input">×</button>
              )}
            </div>
            {startNodeValidation.status !== 'idle' && (
              <span className={`validation-message ${startNodeValidation.status}`}>
                {startNodeValidation.message}
              </span>
            )}
          </div>
          
          <div className="node-input-group">
            <label className="node-label">Goal Node:</label>
            <div className="input-with-validation">
              <input
                type="text"
                value={goalNodeInput}
                onChange={(e) => handleGoalNodeInputChange(e.target.value)}
                placeholder="Enter node ID or click on map"
                disabled={isSearching}
                className={`node-input ${goalNodeValidation.status === 'valid' ? 'valid' : ''} ${goalNodeValidation.status === 'invalid' ? 'invalid' : ''}`}
              />
              {goalNode && !isSearching && (
                <button onClick={handleClearGoal} className="btn-clear-input">×</button>
              )}
            </div>
            {goalNodeValidation.status !== 'idle' && (
              <span className={`validation-message ${goalNodeValidation.status}`}>
                {goalNodeValidation.message}
              </span>
            )}
          </div>

          {reachabilityCheck.status !== 'idle' && (
            <div className={`reachability-message ${reachabilityCheck.status}`}>
              {reachabilityCheck.message}
            </div>
          )}
        </div>
      </div>

      <div className="control-section">
        <h3>Search Control</h3>
        {reachabilityCheck.status === 'unreachable' && (
          <div className="warning-message" style={{ marginBottom: '12px', padding: '10px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', fontSize: '12px', color: 'var(--accent-error)' }}>
            ⚠ Cannot start search: {reachabilityCheck.message}
          </div>
        )}
        <button
          onClick={beginSearch}
          disabled={!canSearch}
          className="btn-primary"
          title={!canSearch && reachabilityCheck.status === 'unreachable' ? reachabilityCheck.message : ''}
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

      {searchCompleted && getAccumulatedData().hasSolution && (
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

