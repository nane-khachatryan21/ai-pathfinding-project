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
    reachabilityCheck,
    searchError,
  } = useSearch();

  const [isGraphInfoCollapsed, setIsGraphInfoCollapsed] = React.useState(false);
  const [isSearchStatsCollapsed, setIsSearchStatsCollapsed] = React.useState(false);

  const currentStepData = getCurrentStepData();
  const accumulatedData = getAccumulatedData();
  const hasSolution = accumulatedData.hasSolution;

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
    if (searchCompleted && hasSolution) {
      // Find the goal_found step to get the solution details
      const goalStep = searchSteps.find(step => step.event === 'goal_found');
      if (goalStep && goalStep.solution_path) {
        result.searchInfo.pathLength = goalStep.solution_path.length;
        if (goalStep.path_cost !== undefined) {
          result.searchInfo.pathCost = goalStep.path_cost;
        }
      }
    }

    return result;
  }, [graphData, searchSteps, currentStep, accumulatedData, currentStepData, searchCompleted, hasSolution]);

  return (
    <div className="stats-panel">
      <div className="stats-section">
        <h3 
          className="collapsible-header" 
          onClick={() => setIsGraphInfoCollapsed(!isGraphInfoCollapsed)}
        >
          <span className="chevron">{isGraphInfoCollapsed ? '▶' : '▼'}</span>
          Graph Information
        </h3>
        {!isGraphInfoCollapsed && (
          <div className="collapsible-content">
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
        )}
      </div>

      {searchSteps.length > 0 && (
        <div className="stats-section">
          <h3 
            className="collapsible-header" 
            onClick={() => setIsSearchStatsCollapsed(!isSearchStatsCollapsed)}
          >
            <span className="chevron">{isSearchStatsCollapsed ? '▶' : '▼'}</span>
            Search Statistics
          </h3>
          {!isSearchStatsCollapsed && (
            <div className="collapsible-content">
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

      {searchCompleted && hasSolution && (
        <div className="stats-section">
          <div className="success-message">
            ✓ Solution Found!
          </div>
        </div>
      )}

      {searchCompleted && !hasSolution && (
        <div className="stats-section">
          <div className="error-message">
            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
              ✗ No Solution Found
            </div>
            <div style={{ fontSize: '12px', fontWeight: 'normal', lineHeight: '1.4' }}>
              {searchError 
                ? `Error: ${searchError}`
                : reachabilityCheck.status === 'unreachable' 
                ? 'The selected nodes are not connected in the graph. Please select different nodes that are part of the same network.'
                : searchSteps.length === 0
                ? 'The search failed to start. Please check your node selections and try again.'
                : 'The algorithm could not find a path between the selected nodes. This may indicate that the nodes are in disconnected components of the graph.'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;

