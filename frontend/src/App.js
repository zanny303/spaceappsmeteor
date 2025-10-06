// src/App.js - FIXED VERSION
import React, { useState, useEffect } from 'react';
import SolarSystem3D from './components/SolarSystem3D';
import ImpactMap from './components/ImpactMap';
import MissionControls from './components/MissionControls';
import ResultsPanel from './components/ResultsPanel';
import AIChatPanel from './components/AIChatPanel';
import LoadingSpinner from './components/LoadingSpinner';
import { analyzeAsteroid, simulateDeflection, healthCheck } from './services/api';
import './styles/App.css';

function App() {
  const [currentAsteroid, setCurrentAsteroid] = useState('99942');
  const [missionPlan, setMissionPlan] = useState(null);
  const [safeTrajectory, setSafeTrajectory] = useState(null);
  const [realTimeDeflection, setRealTimeDeflection] = useState(null); // NEW: Real-time preview
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deflectionParams, setDeflectionParams] = useState({
    dv: 0.005,
    interceptorMass: 500
  });
  const [systemStatus, setSystemStatus] = useState('checking');

  // Check backend health on startup
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck();
        setSystemStatus('healthy');
        handleAsteroidAnalysis(currentAsteroid);
      } catch (err) {
        setSystemStatus('unhealthy');
        setError('Backend server is unavailable. Please ensure the backend is running on port 5000.');
      }
    };
    checkHealth();
  }, []);

  const handleAsteroidAnalysis = async (asteroidId) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeAsteroid(asteroidId);
      setMissionPlan(result);
      setCurrentAsteroid(asteroidId);
      setSafeTrajectory(null);
      setRealTimeDeflection(null); // Reset real-time preview
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeflectionSimulation = async () => {
    if (!missionPlan) return;
    
    setLoading(true);
    try {
      const result = await simulateDeflection({
        initial_state_vector: missionPlan.initial_state_vector,
        required_dv_ms: deflectionParams.dv,
        asteroid_mass_kg: missionPlan.asteroid_info.mass_kg
      });
      setSafeTrajectory(result.safe_trajectory);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeflectionParamChange = (param, value) => {
    setDeflectionParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  // NEW: Real-time deflection preview (called when sliders move)
  const handleRealTimeDeflectionChange = async (params) => {
    if (!missionPlan) return;
    
    try {
      // Call backend for real-time deflection calculation
      const result = await simulateDeflection({
        initial_state_vector: missionPlan.initial_state_vector,
        required_dv_ms: params.dv,
        asteroid_mass_kg: missionPlan.asteroid_info.mass_kg
      });
      setRealTimeDeflection(result.safe_trajectory);
    } catch (err) {
      console.error('Real-time deflection preview failed:', err);
      // Don't show error to user for real-time preview failures
    }
  };

  const handleQuickAsteroid = (asteroidId, name) => {
    setCurrentAsteroid(asteroidId);
    handleAsteroidAnalysis(asteroidId);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🚀 Planetary Defense AI</h1>
          <p>AI-Enhanced Asteroid Threat Assessment & Mitigation System</p>
          <div className="system-status">
            <span className={`status-indicator ${systemStatus}`}></span>
            System: {systemStatus === 'healthy' ? 'Operational' : systemStatus === 'checking' ? 'Checking...' : 'Offline'}
          </div>
        </div>
        <div className="header-actions">
          <div className="quick-asteroids">
            <span>Quick Analysis:</span>
            <button 
              className="btn-primary"
              onClick={() => handleQuickAsteroid('99942', 'Apophis')}
              disabled={loading}
            >
              🎯 Apophis
            </button>
            <button 
              className="btn-secondary"
              onClick={() => handleQuickAsteroid('101955', 'Bennu')}
              disabled={loading}
            >
              ⚫ Bennu
            </button>
            <button 
              className="btn-secondary"
              onClick={() => handleQuickAsteroid('25143', 'Itokawa')}
              disabled={loading}
            >
              🔴 Itokawa
            </button>
          </div>
        </div>
      </header>

      <div className="app-main">
        {/* Left Panel - 3D Visualization */}
        <div className="visualization-panel">
          <div className="panel-header">
            <h2>🌌 3D Solar System & Trajectory Visualization</h2>
            <div className="panel-subtitle">
              Real-time orbital mechanics simulation with hazard corridors
            </div>
          </div>
          <SolarSystem3D 
            missionPlan={missionPlan}
            safeTrajectory={safeTrajectory}
            realTimeDeflection={realTimeDeflection}
            loading={loading}
          />
        </div>

        {/* Right Panel - Controls & Results */}
        <div className="control-panel">
          {/* Mission Controls - UPDATED with onDeflectionChange */}
          <MissionControls
            deflectionParams={deflectionParams}
            onParamChange={handleDeflectionParamChange}
            onSimulate={handleDeflectionSimulation}
            onDeflectionChange={handleRealTimeDeflectionChange}
            loading={loading}
            missionPlan={missionPlan}
          />

          {/* Impact Map */}
          <div className="impact-map-section">
            <div className="panel-header">
              <h2>🗺️ Impact Hazard Assessment</h2>
              <div className="panel-subtitle">
                Global impact consequence visualization
              </div>
            </div>
            <ImpactMap 
              missionPlan={missionPlan}
              safeTrajectory={safeTrajectory}
            />
          </div>

          {/* AI Results */}
          {missionPlan && (
            <ResultsPanel missionPlan={missionPlan} />
          )}

          {/* AI Chat Assistant */}
          <AIChatPanel missionPlan={missionPlan} />
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && <LoadingSpinner />}

      {/* Error Display */}
      {error && (
        <div className="error-overlay">
          <div className="error-message">
            <h3>⚠️ System Error</h3>
            <p>{error}</p>
            <div className="error-actions">
              <button onClick={() => setError(null)}>Dismiss</button>
              <button onClick={() => window.location.reload()}>Reload Page</button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>
            <strong>AI-Enhanced Planetary Defense System </strong> | 
            | 
            Built with React, Three.js, and Python
          </p>
          <div className="footer-links">
            <span>Backend: http://localhost:5000</span>
            <span>Frontend: http://localhost:3000</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;