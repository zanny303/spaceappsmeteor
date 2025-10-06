// src/components/MissionControls.js - Updated version

import React from 'react';
import { Play, Square, Download, Settings, Zap, Target } from 'lucide-react';

const MissionControls = ({ 
  deflectionParams, 
  onParamChange, 
  onSimulate, 
  onDeflectionChange,
  loading, 
  missionPlan 
}) => {
  const handleSliderChange = (param, value) => {
    const newValue = parseFloat(value);
    const newParams = {
      ...deflectionParams,
      [param]: newValue
    };
    
    // Update local state
    onParamChange(param, newValue);
    
    // Trigger real-time deflection preview
    if (onDeflectionChange && missionPlan) {
      onDeflectionChange(newParams);
    }
  };

  const handleSimulate = async () => {
    if (!missionPlan) return;
    
    // Call parent with current slider values for full simulation
    onSimulate(deflectionParams);
  };

  const generatePDF = async () => {
    if (!missionPlan) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/generate_pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(missionPlan)
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `NASA_Defense_Briefing_${missionPlan.asteroid_info.name.replace(/\s+/g, '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        throw new Error('PDF generation failed');
      }
    } catch (error) {
      console.error('PDF generation failed:', error);
      alert('Failed to generate PDF. Please ensure the backend server is running.');
    }
  };

  const exportMissionData = () => {
    if (!missionPlan) return;
    
    const dataStr = JSON.stringify(missionPlan, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(dataBlob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `mission_data_${missionPlan.asteroid_info.name.replace(/\s+/g, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Calculate real-time deflection metrics
  const calculateDeflectionMetrics = () => {
    if (!missionPlan) return null;
    
    const { dv, interceptorMass } = deflectionParams;
    const asteroidMass = missionPlan.asteroid_info.mass_kg;
    
    // DART mission physics: beta factor of 3.6 for momentum enhancement
    const betaFactor = 3.6;
    const efficiency = 0.85;
    
    const momentumRatio = (interceptorMass * efficiency) / asteroidMass;
    const effectiveDv = dv * betaFactor * momentumRatio;
    
    const originalMissDistance = 31664.5; // Default Apophis miss distance in km
    const timeToImpact = missionPlan.mission_parameters.lti_days * 24 * 3600; // seconds
    const newMissDistance = originalMissDistance + (effectiveDv * timeToImpact * 3.6); // km
    
    return {
      effectiveDv,
      momentumTransfer: momentumRatio * 100,
      newMissDistance,
      deflectionEfficiency: betaFactor * efficiency
    };
  };

  const deflectionMetrics = missionPlan ? calculateDeflectionMetrics() : null;

  return (
    <div className="mission-controls">
      <div className="panel-header">
        <h2>🎮 Mission Control Center</h2>
        <div className="panel-subtitle">
          Real-time deflection simulation & parameters
        </div>
      </div>

      {/* Real-time Deflection Controls */}
      <div className="control-group">
        <label htmlFor="dv-slider">
          🚀 Velocity Change (ΔV): <strong>{deflectionParams.dv.toFixed(6)} m/s</strong>
        </label>
        <input
          id="dv-slider"
          type="range"
          min="0.000001"
          max="0.1"
          step="0.000001"
          value={deflectionParams.dv}
          onChange={(e) => handleSliderChange('dv', e.target.value)}
          className="slider"
        />
        <div className="slider-labels">
          <span>Minimal (0.000001 m/s)</span>
          <span>Aggressive (0.1 m/s)</span>
        </div>
        <div className="slider-description">
          Real-time adjustment: Small velocity changes create large trajectory differences over time
        </div>
      </div>

      <div className="control-group">
        <label htmlFor="mass-slider">
          ⚖️ Interceptor Mass: <strong>{deflectionParams.interceptorMass} kg</strong>
        </label>
        <input
          id="mass-slider"
          type="range"
          min="100"
          max="10000"
          step="100"
          value={deflectionParams.interceptorMass}
          onChange={(e) => handleSliderChange('interceptorMass', e.target.value)}
          className="slider"
        />
        <div className="slider-labels">
          <span>Small (100 kg)</span>
          <span>Large (10,000 kg)</span>
        </div>
        <div className="slider-description">
          Larger impactors transfer more momentum via enhanced kinetic impact (DART-style)
        </div>
      </div>

      {/* Real-time Deflection Preview */}
      {missionPlan && deflectionMetrics && (
        <div className="deflection-preview">
          <div className="preview-header">
            <Zap size={16} />
            <h4>🎯 Real-time Deflection Preview</h4>
          </div>
          <div className="deflection-stats">
            <div className="stat">
              <span>Effective ΔV:</span>
              <span className="highlight">{deflectionMetrics.effectiveDv.toFixed(8)} m/s</span>
            </div>
            <div className="stat">
              <span>Momentum Transfer:</span>
              <span className="highlight">{deflectionMetrics.momentumTransfer.toFixed(6)}%</span>
            </div>
            <div className="stat">
              <span>New Miss Distance:</span>
              <span className="highlight">{deflectionMetrics.newMissDistance.toFixed(0)} km</span>
            </div>
            <div className="stat">
              <span>Deflection Efficiency:</span>
              <span className="highlight">{deflectionMetrics.deflectionEfficiency.toFixed(1)}x</span>
            </div>
          </div>
          <div className="deflection-visual">
            <div className="trajectory-comparison">
              <div className="trajectory original">
                <div className="trajectory-label">Original</div>
                <div className="trajectory-line"></div>
                <div className="miss-distance">~31,664 km</div>
              </div>
              <div className="trajectory deflected">
                <div className="trajectory-label">Deflected</div>
                <div className="trajectory-line deflected"></div>
                <div className="miss-distance safe">{deflectionMetrics.newMissDistance.toFixed(0)} km</div>
              </div>
            </div>
          </div>
          <div className="deflection-note">
            💡 <strong>Live Preview:</strong> Yellow trajectory in 3D view shows deflection effect
          </div>
        </div>
      )}

      <div className="control-buttons">
        <button
          onClick={handleSimulate}
          disabled={loading || !missionPlan}
          className="btn-simulate"
        >
          {loading ? <Square size={16} /> : <Play size={16} />}
          {loading ? 'Running Full Simulation...' : 'Run High-Precision Simulation'}
        </button>

        <div className="button-group">
          <button
            onClick={generatePDF}
            disabled={!missionPlan}
            className="btn-download"
          >
            <Download size={16} />
            Download PDF Briefing
          </button>

          <button
            onClick={exportMissionData}
            disabled={!missionPlan}
            className="btn-export"
          >
            <Settings size={16} />
            Export Data
          </button>
        </div>
      </div>

      {/* Mission Status */}
      {missionPlan && (
        <div className="mission-info">
          <div className="mission-status-header">
            <Target size={16} />
            <h4>📊 Mission Status & Parameters</h4>
          </div>
          <div className="param-grid">
            <div className="param-item">
              <span className="param-label">Asteroid:</span>
              <span className="param-value">{missionPlan.asteroid_info.name}</span>
            </div>
            <div className="param-item">
              <span className="param-label">Diameter:</span>
              <span className="param-value">{missionPlan.asteroid_info.diameter_m.toFixed(1)} m</span>
            </div>
            <div className="param-item">
              <span className="param-label">Mass:</span>
              <span className="param-value">{missionPlan.asteroid_info.mass_kg.toExponential(2)} kg</span>
            </div>
            <div className="param-item">
              <span className="param-label">Velocity:</span>
              <span className="param-value">{missionPlan.asteroid_info.velocity_kms} km/s</span>
            </div>
            <div className="param-item">
              <span className="param-label">LTI:</span>
              <span className="param-value">{missionPlan.mission_parameters.lti_days} days</span>
            </div>
            <div className="param-item">
              <span className="param-label">Required ΔV:</span>
              <span className="param-value highlight">{missionPlan.mission_parameters.required_dv_ms.toFixed(6)} m/s</span>
            </div>
            <div className="param-item">
              <span className="param-label">Threat Level:</span>
              <span className="param-value threat-high">HIGH</span>
            </div>
            <div className="param-item">
              <span className="param-label">Data Sources:</span>
              <span className="param-value">{missionPlan.asteroid_info.data_sources?.join(', ') || 'Sample Data'}</span>
            </div>
          </div>
          
          {/* Deflection Effectiveness */}
          {deflectionMetrics && (
            <div className="deflection-effectiveness">
              <div className="effectiveness-bar">
                <div 
                  className="effectiveness-fill"
                  style={{ 
                    width: `${Math.min(100, (deflectionMetrics.effectiveDv / missionPlan.mission_parameters.required_dv_ms) * 100)}%` 
                  }}
                ></div>
              </div>
              <div className="effectiveness-label">
                Deflection Power: {((deflectionMetrics.effectiveDv / missionPlan.mission_parameters.required_dv_ms) * 100).toFixed(1)}% of required
              </div>
            </div>
          )}
        </div>
      )}

      {!missionPlan && (
        <div className="no-mission-message">
          <div className="no-mission-icon">🎯</div>
          <p>Select an asteroid to begin mission planning</p>
          <p className="no-mission-subtitle">
            Analyze Apophis, Bennu, or Itokawa to see real-time deflection simulations
          </p>
        </div>
      )}
    </div>
  );
};

export default MissionControls;