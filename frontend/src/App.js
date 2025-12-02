import React from 'react';
import { SearchProvider } from './context/SearchContext';
import MapView from './components/MapView';
import ControlPanel from './components/ControlPanel';
import StatsPanel from './components/StatsPanel';
import './styles/App.css';

function App() {
  return (
    <SearchProvider>
      <div className="app">
        <div className="sidebar">
          <div className="header">
            <h1>Pathfinding Visualization</h1>
            <p className="subtitle">Armenia Road Network</p>
          </div>
          <ControlPanel />
          <StatsPanel />
        </div>
        <div className="map-container">
          <MapView />
        </div>
      </div>
    </SearchProvider>
  );
}

export default App;

