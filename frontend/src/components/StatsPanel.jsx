import React, { useMemo } from 'react';
import { useSearch } from '../context/SearchContext';

const StatsPanel = () => {
  const {
    graphData,
    searchSteps,
    currentStep,
    isSearching,
    searchCompleted,
    getCurrentStepData,
    getAccumulatedData,
  } = useSearch();

  const currentStepData = getCurrentStepData();
  const accumulatedData = getAccumulatedData();

  // Calculate statistics
  const stats = useMemo(() => {
    const result = {
      graphInfo: {
        name: graphData?.metadata?.name || 'N/A',
        nodeCount: graphData?.metadata?.node_count || 0,
        edgeCount: graphData?.metadata?.edge_count || 0,
      },
      searchInfo: {
        currentStep: currentStep + 1,
        totalSteps: searchSteps.length,
        nodesExpanded: accumulatedData.expanded.length,
        frontierSize: accumulatedData.frontier.length,
        pathCost: null,
        pathLength: null,
      },
    };

    // Add path info if solution found
    if (searchCompleted && accumulatedData.solutionPath.length > 0) {
      result.searchInfo.pathLength = accumulatedData.solutionPath.length;
      
      // Get final step cost
      const finalStep = searchSteps[searchSteps.length - 1];
      if (finalStep && finalStep.path_cost !== undefined) {
        result.searchInfo.pathCost = finalStep.path_cost;
      }
    }

    return result;
  }, [graphData, searchSteps, currentStep, accumulatedData, currentStepData, searchCompleted]);

  return (
    <div className="stats-panel">
      <div className="stats-section">
        <h3>Graph Information</h3>
        <div className="stat-item">
          <span className="stat-label">Graph:</span>
          <span className="stat-value">{stats.graphInfo.name}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Nodes:</span>
          <span className="stat-value">{stats.graphInfo.nodeCount.toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Edges:</span>
          <span className="stat-value">{stats.graphInfo.edgeCount.toLocaleString()}</span>
        </div>
      </div>

      {searchSteps.length > 0 && (
        <div className="stats-section">
          <h3>Search Statistics</h3>
          <div className="stat-item">
            <span className="stat-label">Step:</span>
            <span className="stat-value">
              {stats.searchInfo.currentStep} / {stats.searchInfo.totalSteps}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Expanded:</span>
            <span className="stat-value stat-expanded">
              {stats.searchInfo.nodesExpanded}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Frontier:</span>
            <span className="stat-value stat-frontier">
              {stats.searchInfo.frontierSize}
            </span>
          </div>
          {currentStepData && currentStepData.path_cost !== undefined && (
            <div className="stat-item">
              <span className="stat-label">Current Cost:</span>
              <span className="stat-value">
                {currentStepData.path_cost.toFixed(2)} m
              </span>
            </div>
          )}
          {stats.searchInfo.pathLength && (
            <div className="stat-item">
              <span className="stat-label">Path Length:</span>
              <span className="stat-value stat-solution">
                {stats.searchInfo.pathLength} nodes
              </span>
            </div>
          )}
          {stats.searchInfo.pathCost !== null && (
            <div className="stat-item">
              <span className="stat-label">Path Cost:</span>
              <span className="stat-value stat-solution">
                {stats.searchInfo.pathCost.toFixed(2)} m
              </span>
            </div>
          )}
        </div>
      )}

      {isSearching && (
        <div className="stats-section">
          <div className="searching-indicator">
            <div className="spinner"></div>
            <span>Searching...</span>
          </div>
        </div>
      )}

      {searchCompleted && accumulatedData.solutionPath.length > 0 && (
        <div className="stats-section">
          <div className="success-message">
            ✓ Solution Found!
          </div>
        </div>
      )}

      {searchCompleted && accumulatedData.solutionPath.length === 0 && (
        <div className="stats-section">
          <div className="error-message">
            ✗ No Solution Found
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;

