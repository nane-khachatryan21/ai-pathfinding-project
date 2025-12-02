import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, useMap } from 'react-leaflet';
import { useSearch } from '../context/SearchContext';
import 'leaflet/dist/leaflet.css';

// Component to handle map updates
function MapController({ bounds }) {
  const map = useMap();

  useEffect(() => {
    if (bounds && bounds.length === 2) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);

  return null;
}

// Component to handle node click events
function MapClickHandler({ onNodeClick }) {
  const map = useMap();

  useEffect(() => {
    const handleClick = (e) => {
      onNodeClick(e.latlng);
    };

    map.on('click', handleClick);
    return () => {
      map.off('click', handleClick);
    };
  }, [map, onNodeClick]);

  return null;
}

const MapView = () => {
  const {
    graphData,
    startNode,
    setStartNode,
    goalNode,
    setGoalNode,
    handleStartNodeInputChange,
    handleGoalNodeInputChange,
    getAccumulatedData,
    isSearching,
    searchCompleted,
  } = useSearch();

  const [bounds, setBounds] = useState(null);
  const [nodePositions, setNodePositions] = useState({});

  // Calculate bounds and node positions when graph data changes
  useEffect(() => {
    if (graphData && graphData.nodes) {
      const lats = graphData.nodes.map(n => n.lat);
      const lons = graphData.nodes.map(n => n.lon);

      if (lats.length > 0 && lons.length > 0) {
        const minLat = Math.min(...lats);
        const maxLat = Math.max(...lats);
        const minLon = Math.min(...lons);
        const maxLon = Math.max(...lons);

        setBounds([
          [minLat, minLon],
          [maxLat, maxLon],
        ]);
      }

      // Create node position map for quick lookup
      const positions = {};
      graphData.nodes.forEach(node => {
        positions[node.id] = [node.lat, node.lon];
      });
      setNodePositions(positions);
    }
  }, [graphData]);

  // Handle node click
  const handleNodeClick = (latlng) => {
    if (!graphData || isSearching) return;

    // Find closest node to click
    let closestNode = null;
    let minDistance = Infinity;

    graphData.nodes.forEach(node => {
      const distance = Math.sqrt(
        Math.pow(node.lat - latlng.lat, 2) + Math.pow(node.lon - latlng.lng, 2)
      );
      if (distance < minDistance) {
        minDistance = distance;
        closestNode = node.id;
      }
    });

    // Only select if click is reasonably close (within 0.01 degrees)
    if (minDistance < 0.01) {
      if (!startNode) {
        // Use the text input handler to trigger validation
        handleStartNodeInputChange(closestNode);
      } else if (!goalNode && closestNode !== startNode) {
        // Use the text input handler to trigger validation
        handleGoalNodeInputChange(closestNode);
      }
    }
  };

  // Get visualization data
  const accumulatedData = getAccumulatedData();

  if (!graphData) {
    return (
      <div className="map-loading">
        <p>Loading map...</p>
      </div>
    );
  }

  const center = bounds ? [
    (bounds[0][0] + bounds[1][0]) / 2,
    (bounds[0][1] + bounds[1][1]) / 2,
  ] : [40.1872, 44.5152]; // Default to Yerevan

  return (
    <MapContainer
      center={center}
      zoom={8}
      style={{ width: '100%', height: '100%' }}
      className="leaflet-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <MapController bounds={bounds} />
      <MapClickHandler onNodeClick={handleNodeClick} />

      {/* Draw all edges (base layer) */}
      {graphData.edges && graphData.edges.map((edge, idx) => {
        const sourcePos = nodePositions[edge.source];
        const targetPos = nodePositions[edge.target];
        if (sourcePos && targetPos) {
          return (
            <Polyline
              key={`edge-${idx}`}
              positions={[sourcePos, targetPos]}
              color="#555"
              weight={1}
              opacity={0.3}
            />
          );
        }
        return null;
      })}

      {/* Draw solution path */}
      {searchCompleted && accumulatedData.solutionPath.length > 0 && (
        <Polyline
          positions={accumulatedData.solutionPath
            .map(nodeId => nodePositions[nodeId])
            .filter(pos => pos)}
          color="#00ff88"
          weight={4}
          opacity={0.9}
          className="solution-path"
        />
      )}

      {/* Draw expanded nodes */}
      {accumulatedData.expanded.map(nodeId => {
        const pos = nodePositions[nodeId];
        if (pos && nodeId !== startNode && nodeId !== goalNode) {
          return (
            <CircleMarker
              key={`expanded-${nodeId}`}
              center={pos}
              radius={3}
              fillColor="#4a90e2"
              color="#2a5a8a"
              weight={1}
              fillOpacity={0.6}
            />
          );
        }
        return null;
      })}

      {/* Draw frontier nodes */}
      {accumulatedData.frontier.map(nodeId => {
        const pos = nodePositions[nodeId];
        if (pos && nodeId !== startNode && nodeId !== goalNode) {
          return (
            <CircleMarker
              key={`frontier-${nodeId}`}
              center={pos}
              radius={4}
              fillColor="#ffa500"
              color="#ff6600"
              weight={2}
              fillOpacity={0.8}
              className="frontier-node"
            />
          );
        }
        return null;
      })}

      {/* Draw start node */}
      {startNode && nodePositions[startNode] && (
        <CircleMarker
          center={nodePositions[startNode]}
          radius={6}
          fillColor="#00ff00"
          color="#00aa00"
          weight={2}
          fillOpacity={1}
        />
      )}

      {/* Draw goal node */}
      {goalNode && nodePositions[goalNode] && (
        <CircleMarker
          center={nodePositions[goalNode]}
          radius={6}
          fillColor="#ff0000"
          color="#aa0000"
          weight={2}
          fillOpacity={1}
        />
      )}
    </MapContainer>
  );
};

export default MapView;

