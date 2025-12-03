import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import {
  fetchGraphs,
  fetchGraph,
  fetchAlgorithms,
  fetchHeuristics,
  startSearch,
  fetchSearchSteps,
  validateNode,
  checkReachability,
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

  // Node text input and validation
  const [startNodeInput, setStartNodeInput] = useState('');
  const [goalNodeInput, setGoalNodeInput] = useState('');
  const [startNodeValidation, setStartNodeValidation] = useState({ status: 'idle', message: '' });
  const [goalNodeValidation, setGoalNodeValidation] = useState({ status: 'idle', message: '' });
  const [reachabilityCheck, setReachabilityCheck] = useState({ status: 'idle', message: '' });
  const [searchError, setSearchError] = useState(null);
  
  // Refs for debouncing
  const startNodeDebounceRef = useRef(null);
  const goalNodeDebounceRef = useRef(null);

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

  // Validate a node with debouncing
  const validateNodeInput = useCallback(async (nodeId, isStart) => {
    if (!selectedGraph || !nodeId.trim()) {
      if (isStart) {
        setStartNodeValidation({ status: 'idle', message: '' });
      } else {
        setGoalNodeValidation({ status: 'idle', message: '' });
      }
      return;
    }

    // Set validating status
    if (isStart) {
      setStartNodeValidation({ status: 'validating', message: 'Checking...' });
    } else {
      setGoalNodeValidation({ status: 'validating', message: 'Checking...' });
    }

    try {
      const result = await validateNode(selectedGraph, nodeId);
      
      if (result.success && result.valid) {
        if (isStart) {
          setStartNode(result.node_id);
          setStartNodeValidation({ status: 'valid', message: 'Valid node' });
        } else {
          setGoalNode(result.node_id);
          setGoalNodeValidation({ status: 'valid', message: 'Valid node' });
        }
      } else {
        if (isStart) {
          setStartNode(null);
          setStartNodeValidation({ status: 'invalid', message: result.error || 'Node not found' });
        } else {
          setGoalNode(null);
          setGoalNodeValidation({ status: 'invalid', message: result.error || 'Node not found' });
        }
      }
    } catch (error) {
      if (isStart) {
        setStartNode(null);
        setStartNodeValidation({ status: 'invalid', message: 'Validation failed' });
      } else {
        setGoalNode(null);
        setGoalNodeValidation({ status: 'invalid', message: 'Validation failed' });
      }
    }
  }, [selectedGraph]);

  // Handle start node input change with debouncing
  const handleStartNodeInputChange = useCallback((value) => {
    setStartNodeInput(value);
    
    // Clear previous timeout
    if (startNodeDebounceRef.current) {
      clearTimeout(startNodeDebounceRef.current);
    }
    
    // Debounce validation
    startNodeDebounceRef.current = setTimeout(() => {
      validateNodeInput(value, true);
    }, 500);
  }, [validateNodeInput]);

  // Handle goal node input change with debouncing
  const handleGoalNodeInputChange = useCallback((value) => {
    setGoalNodeInput(value);
    
    // Clear previous timeout
    if (goalNodeDebounceRef.current) {
      clearTimeout(goalNodeDebounceRef.current);
    }
    
    // Debounce validation
    goalNodeDebounceRef.current = setTimeout(() => {
      validateNodeInput(value, false);
    }, 500);
  }, [validateNodeInput]);

  // Check reachability between start and goal
  const checkNodesReachability = useCallback(async () => {
    if (!selectedGraph || !startNode || !goalNode) {
      setReachabilityCheck({ status: 'idle', message: '' });
      return;
    }

    setReachabilityCheck({ status: 'checking', message: 'Checking connectivity...' });

    try {
      const result = await checkReachability(selectedGraph, startNode, goalNode);
      
      if (result.success && result.reachable) {
        setReachabilityCheck({ status: 'reachable', message: 'Nodes are connected' });
      } else {
        setReachabilityCheck({ 
          status: 'unreachable', 
          message: result.error || 'Nodes are not connected' 
        });
      }
    } catch (error) {
      setReachabilityCheck({ status: 'error', message: 'Failed to check connectivity' });
    }
  }, [selectedGraph, startNode, goalNode]);

  // Check reachability when both nodes are selected
  useEffect(() => {
    if (startNode && goalNode) {
      checkNodesReachability();
    } else {
      setReachabilityCheck({ status: 'idle', message: '' });
    }
  }, [startNode, goalNode, checkNodesReachability]);

  // Update text inputs when nodes are selected via map
  useEffect(() => {
    if (startNode && startNode !== startNodeInput) {
      setStartNodeInput(startNode);
      setStartNodeValidation({ status: 'valid', message: 'Valid node' });
    }
  }, [startNode]);

  useEffect(() => {
    if (goalNode && goalNode !== goalNodeInput) {
      setGoalNodeInput(goalNode);
      setGoalNodeValidation({ status: 'valid', message: 'Valid node' });
    }
  }, [goalNode]);

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
      setSearchError(null); // Clear any previous errors

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
      setSearchError(error.message || 'Failed to start search');
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
            
            // Check for backend error
            if (response.error) {
              setSearchError(response.error);
              console.error('Search error:', response.error);
            }
            
            // Advance to the last step to show final results
            if (response.total_steps > 0) {
              setCurrentStep(response.total_steps - 1);
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch search steps:', error);
        clearInterval(pollInterval);
        setIsSearching(false);
        setSearchError(error.message || 'Failed to fetch search results');
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
    setReachabilityCheck({ status: 'idle', message: '' });
    setSearchError(null);
  }, []);

  // Animation controls
  const play = useCallback(() => {
    if (currentStep >= searchSteps.length - 1) {
      return; // Already at the end
    }
    
    setIsPlaying(true);
    animator.start(() => {
      let shouldContinue = true;
      setCurrentStep(prev => {
        if (prev >= searchSteps.length - 1) {
          setIsPlaying(false);
          shouldContinue = false;
          return prev;
        }
        return prev + 1;
      });
      return shouldContinue;
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

  // Check if solution exists in the entire search
  const hasSolution = useCallback(() => {
    return searchSteps.some(step => step.event === 'goal_found' && step.solution_path && step.solution_path.length > 0);
  }, [searchSteps]);

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
      hasSolution: hasSolution(),
    };
  }, [currentStep, searchSteps, hasSolution]);

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

    // Node input and validation
    startNodeInput,
    goalNodeInput,
    handleStartNodeInputChange,
    handleGoalNodeInputChange,
    startNodeValidation,
    goalNodeValidation,
    reachabilityCheck,

    // Graph data
    graphData,
    loading,

    // Search state
    sessionId,
    searchSteps,
    currentStep,
    isSearching,
    searchCompleted,
    searchError,

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

