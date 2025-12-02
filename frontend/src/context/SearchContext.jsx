import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  fetchGraphs,
  fetchGraph,
  fetchAlgorithms,
  fetchHeuristics,
  startSearch,
  fetchSearchSteps,
} from '../services/api';
import animator from '../utils/animator';

const SearchContext = createContext();

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error('useSearch must be used within SearchProvider');
  }
  return context;
};

export const SearchProvider = ({ children }) => {
  // Available options
  const [graphs, setGraphs] = useState([]);
  const [algorithms, setAlgorithms] = useState([]);
  const [heuristics, setHeuristics] = useState([]);

  // Current selections
  const [selectedGraph, setSelectedGraph] = useState(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState(null);
  const [selectedHeuristic, setSelectedHeuristic] = useState(null);
  const [startNode, setStartNode] = useState(null);
  const [goalNode, setGoalNode] = useState(null);

  // Graph data
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Search state
  const [sessionId, setSessionId] = useState(null);
  const [searchSteps, setSearchSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [searchCompleted, setSearchCompleted] = useState(false);

  // Animation state
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1); // 1x to 100x

  // Initialize - load available options
  useEffect(() => {
    const initialize = async () => {
      try {
        setLoading(true);
        const [graphsRes, algorithmsRes, heuristicsRes] = await Promise.all([
          fetchGraphs(),
          fetchAlgorithms(),
          fetchHeuristics(),
        ]);

        if (graphsRes.success) {
          setGraphs(graphsRes.graphs);
          // Select first graph by default
          if (graphsRes.graphs.length > 0) {
            setSelectedGraph(graphsRes.graphs[0].graph_id);
          }
        }

        if (algorithmsRes.success) {
          setAlgorithms(algorithmsRes.algorithms);
          // Select first algorithm by default
          if (algorithmsRes.algorithms.length > 0) {
            setSelectedAlgorithm(algorithmsRes.algorithms[0].name);
          }
        }

        if (heuristicsRes.success) {
          setHeuristics(heuristicsRes.heuristics);
          // Select first heuristic by default
          if (heuristicsRes.heuristics.length > 0) {
            setSelectedHeuristic(heuristicsRes.heuristics[0].name);
          }
        }
      } catch (error) {
        console.error('Failed to initialize:', error);
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, []);

  // Load graph data when selection changes
  useEffect(() => {
    const loadGraph = async () => {
      if (!selectedGraph) return;

      try {
        setLoading(true);
        const response = await fetchGraph(selectedGraph);
        if (response.success) {
          setGraphData(response.data);
          // Reset selections when graph changes
          setStartNode(null);
          setGoalNode(null);
          resetSearch();
        }
      } catch (error) {
        console.error('Failed to load graph:', error);
      } finally {
        setLoading(false);
      }
    };

    loadGraph();
  }, [selectedGraph]);

  // Start a new search
  const beginSearch = useCallback(async () => {
    if (!selectedGraph || !selectedAlgorithm || !startNode || !goalNode) {
      console.error('Missing required parameters for search');
      return;
    }

    const currentAlgo = algorithms.find(a => a.name === selectedAlgorithm);
    if (currentAlgo?.requires_heuristic && !selectedHeuristic) {
      console.error('Algorithm requires a heuristic');
      return;
    }

    try {
      setIsSearching(true);
      setSearchCompleted(false);
      setSearchSteps([]);
      setCurrentStep(0);

      const searchParams = {
        graph_id: selectedGraph,
        algorithm: selectedAlgorithm,
        start_node: startNode,
        goal_node: goalNode,
      };

      if (currentAlgo?.requires_heuristic) {
        searchParams.heuristic = selectedHeuristic;
      }

      const response = await startSearch(searchParams);
      if (response.success) {
        setSessionId(response.session_id);
        pollSearchProgress(response.session_id);
      }
    } catch (error) {
      console.error('Failed to start search:', error);
      setIsSearching(false);
    }
  }, [selectedGraph, selectedAlgorithm, selectedHeuristic, startNode, goalNode, algorithms]);

  // Poll for search progress
  const pollSearchProgress = useCallback(async (sid) => {
    let offset = 0;
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetchSearchSteps(sid, offset);
        if (response.success) {
          if (response.steps.length > 0) {
            setSearchSteps(prev => [...prev, ...response.steps]);
            offset = response.total_steps;
          }

          if (response.completed) {
            clearInterval(pollInterval);
            setIsSearching(false);
            setSearchCompleted(true);
            setIsPlaying(false);
          }
        }
      } catch (error) {
        console.error('Failed to fetch search steps:', error);
        clearInterval(pollInterval);
        setIsSearching(false);
      }
    }, 100); // Poll every 100ms
  }, []);

  // Reset search
  const resetSearch = useCallback(() => {
    setSessionId(null);
    setSearchSteps([]);
    setCurrentStep(0);
    setIsSearching(false);
    setSearchCompleted(false);
    setIsPlaying(false);
  }, []);

  // Animation controls
  const play = useCallback(() => {
    setIsPlaying(true);
    animator.start(() => {
      setCurrentStep(prev => {
        if (prev >= searchSteps.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
      return currentStep < searchSteps.length - 1;
    }, speed);
  }, [currentStep, searchSteps.length, speed]);

  const pause = useCallback(() => {
    setIsPlaying(false);
    animator.stop();
  }, []);

  // Update animator speed when speed changes
  useEffect(() => {
    if (isPlaying) {
      animator.setSpeed(speed);
    }
  }, [speed, isPlaying]);

  // Stop animator when component unmounts
  useEffect(() => {
    return () => {
      animator.stop();
    };
  }, []);

  const stepForward = useCallback(() => {
    setCurrentStep(prev => Math.min(prev + 1, searchSteps.length - 1));
  }, [searchSteps.length]);

  const stepBackward = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, []);

  const goToStep = useCallback((step) => {
    setCurrentStep(Math.max(0, Math.min(step, searchSteps.length - 1)));
  }, [searchSteps.length]);

  // Get current step data
  const getCurrentStepData = useCallback(() => {
    if (currentStep >= 0 && currentStep < searchSteps.length) {
      return searchSteps[currentStep];
    }
    return null;
  }, [currentStep, searchSteps]);

  // Get accumulated data up to current step
  const getAccumulatedData = useCallback(() => {
    const frontier = new Set();
    const expanded = new Set();
    let solutionPath = [];

    for (let i = 0; i <= currentStep && i < searchSteps.length; i++) {
      const step = searchSteps[i];
      
      // Add to expanded
      if (step.current_node) {
        expanded.add(step.current_node);
      }
      
      // Update frontier
      if (step.frontier) {
        step.frontier.forEach(node => frontier.add(node));
      }
      
      // Remove expanded from frontier
      if (step.current_node) {
        frontier.delete(step.current_node);
      }
      
      // Check for solution
      if (step.event === 'goal_found' && step.solution_path) {
        solutionPath = step.solution_path;
      }
    }

    return {
      frontier: Array.from(frontier),
      expanded: Array.from(expanded),
      solutionPath,
    };
  }, [currentStep, searchSteps]);

  const value = {
    // Available options
    graphs,
    algorithms,
    heuristics,

    // Current selections
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

    // Graph data
    graphData,
    loading,

    // Search state
    sessionId,
    searchSteps,
    currentStep,
    isSearching,
    searchCompleted,

    // Animation
    isPlaying,
    speed,
    setSpeed,

    // Actions
    beginSearch,
    resetSearch,
    play,
    pause,
    stepForward,
    stepBackward,
    goToStep,

    // Helpers
    getCurrentStepData,
    getAccumulatedData,
  };

  return <SearchContext.Provider value={value}>{children}</SearchContext.Provider>;
};

