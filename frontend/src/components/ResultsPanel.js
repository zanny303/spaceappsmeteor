// src/components/ResultsPanel.js - COMPLETE FIX
import React from 'react';
import { Brain, AlertTriangle, CheckCircle, Target, Shield, Zap } from 'lucide-react';

const ResultsPanel = ({ missionPlan }) => {
  if (!missionPlan) return null;

  const { mission_recommendation, ai_predicted_consequences, mission_parameters } = missionPlan;

  // FIXED: Robust number formatting with null/undefined/NaN checks
  const formatNumber = (num, decimals = 1) => {
    if (num === null || num === undefined) return 'N/A';
    if (isNaN(num)) return 'Invalid';
    if (!isFinite(num)) return 'Overflow';
    const parsed = Number(num);
    if (isNaN(parsed)) return 'N/A';
    return parsed.toFixed(decimals);
  };

  const formatLargeNumber = (num) => {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    if (!isFinite(num)) return 'Overflow';
    const parsed = Number(num);
    if (isNaN(parsed)) return 'N/A';
    
    if (parsed >= 1e12) return `$${(parsed / 1e12).toFixed(1)} Trillion`;
    if (parsed >= 1e9) return `$${(parsed / 1e9).toFixed(1)} Billion`;
    if (parsed >= 1e6) return `$${(parsed / 1e6).toFixed(1)} Million`;
    return `$${parsed.toLocaleString()}`;
  };

  const formatCasualties = (num) => {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    if (!isFinite(num)) return 'Overflow';
    const parsed = Number(num);
    if (isNaN(parsed)) return 'N/A';
    
    if (parsed >= 1e6) return `${(parsed / 1e6).toFixed(1)} Million`;
    if (parsed >= 1e3) return `${(parsed / 1e3).toFixed(1)} Thousand`;
    return parsed.toLocaleString();
  };

  // FIXED: Lead time display with proper handling
  const formatLeadTime = (days) => {
    if (days === null || days === undefined || isNaN(days)) return 'Unknown';
    if (!isFinite(days)) return 'Invalid';
    
    const parsed = Number(days);
    if (isNaN(parsed)) return 'Unknown';
    
    if (parsed < 1) return 'CRITICAL: < 1 day';
    if (parsed < 30) return `${Math.round(parsed)} days (URGENT)`;
    if (parsed < 365) return `${Math.round(parsed)} days (${(parsed / 30).toFixed(1)} months)`;
    return `${parsed.toLocaleString()} days (${(parsed / 365).toFixed(1)} years)`;
  };

  const getSeverityLevel = (value, thresholds) => {
    if (value === null || value === undefined || isNaN(value)) return 'unknown';
    if (value >= thresholds.critical) return 'critical';
    if (value >= thresholds.high) return 'high';
    if (value >= thresholds.medium) return 'medium';
    return 'low';
  };

  const severityThresholds = {
    energy: { critical: 1000, high: 100, medium: 10 },
    damage: { critical: 1e12, high: 1e11, medium: 1e10 },
    casualties: { critical: 1000000, high: 100000, medium: 10000 },
    seismic: { critical: 8, high: 7, medium: 6 }
  };

  // FIXED: Calculate difficulty with validation
  const calculateDifficulty = (params) => {
    if (!params) return 'UNKNOWN';
    
    const lti_days = params.lti_days ?? 0;
    const required_dv_ms = params.required_dv_ms ?? 0;
    const calculated_mass_kg = params.calculated_mass_kg ?? 0;
    
    let score = 0;
    
    // Time factor
    if (lti_days < 180) score += 3;
    else if (lti_days < 365) score += 2;
    else if (lti_days < 730) score += 1;
    
    // Delta-V factor
    if (required_dv_ms > 0.02) score += 3;
    else if (required_dv_ms > 0.01) score += 2;
    else if (required_dv_ms > 0.005) score += 1;
    
    // Mass factor
    if (calculated_mass_kg > 1e12) score += 2;
    else if (calculated_mass_kg > 1e11) score += 1;
    
    if (score >= 6) return 'VERY HIGH';
    if (score >= 4) return 'HIGH';
    if (score >= 2) return 'MEDIUM';
    return 'LOW';
  };

  return (
    <div className="results-panel">
      <div className="panel-header">
        <h2>AI Analysis Results</h2>
        <div className="panel-subtitle">
          Machine learning powered threat assessment
        </div>
      </div>

      {/* Mission Recommendation */}
      <div className="result-section">
        <div className="section-header">
          <Brain size={20} />
          <h3>AI Mission Recommendation</h3>
          <div className="confidence-badge">
            {formatNumber(mission_recommendation?.confidence_score ?? 0, 1)}% Confidence
          </div>
        </div>
        
        <div className="recommendation-card">
          <div className="mission-architecture">
            <Target size={18} />
            <strong className="architecture-source">{mission_recommendation?.source ?? 'Unknown'}</strong>
            <span className="separator">→</span>
            <strong className="architecture-type">{mission_recommendation?.interceptor_type ?? 'Unknown'}</strong>
          </div>
          
          <div className="rationale">
            <p>{mission_recommendation?.rationale ?? 'No rationale available.'}</p>
          </div>
          
          <div className="model-info">
            <Shield size={12} />
            Model: {(mission_recommendation?.model_type ?? 'unknown').replace('_', ' ').toUpperCase()}
            {mission_recommendation?.features_used && (
              <span className="features"> • Features: {mission_recommendation.features_used.join(', ')}</span>
            )}
          </div>
        </div>
      </div>

      {/* Impact Consequences */}
      <div className="result-section">
        <div className="section-header">
          <AlertTriangle size={20} />
          <h3>Predicted Impact Consequences</h3>
        </div>

        <div className="consequences-grid">
          <div className={`consequence-item ${getSeverityLevel(ai_predicted_consequences?.impact_energy_megatons ?? 0, severityThresholds.energy)}`}>
            <div className="consequence-icon">💥</div>
            <div className="consequence-content">
              <div className="consequence-label">Kinetic Energy</div>
              <div className="consequence-value">
                {formatNumber(ai_predicted_consequences?.impact_energy_megatons ?? 0, 1)} MT TNT
              </div>
              <div className="consequence-severity">
                {getSeverityLevel(ai_predicted_consequences?.impact_energy_megatons ?? 0, severityThresholds.energy).toUpperCase()}
              </div>
            </div>
          </div>

          <div className={`consequence-item ${getSeverityLevel(ai_predicted_consequences?.economic_damage_usd ?? 0, severityThresholds.damage)}`}>
            <div className="consequence-icon">💸</div>
            <div className="consequence-content">
              <div className="consequence-label">Economic Damage</div>
              <div className="consequence-value">
                {formatLargeNumber(ai_predicted_consequences?.economic_damage_usd ?? 0)}
              </div>
              <div className="consequence-severity">
                {getSeverityLevel(ai_predicted_consequences?.economic_damage_usd ?? 0, severityThresholds.damage).toUpperCase()}
              </div>
            </div>
          </div>

          <div className={`consequence-item ${getSeverityLevel(ai_predicted_consequences?.predicted_casualties ?? 0, severityThresholds.casualties)}`}>
            <div className="consequence-icon">👥</div>
            <div className="consequence-content">
              <div className="consequence-label">Predicted Casualties</div>
              <div className="consequence-value">
                {formatCasualties(ai_predicted_consequences?.predicted_casualties ?? 0)}
              </div>
              <div className="consequence-severity">
                {getSeverityLevel(ai_predicted_consequences?.predicted_casualties ?? 0, severityThresholds.casualties).toUpperCase()}
              </div>
            </div>
          </div>

          <div className={`consequence-item ${getSeverityLevel(ai_predicted_consequences?.predicted_seismic_magnitude ?? 0, severityThresholds.seismic)}`}>
            <div className="consequence-icon">🏔️</div>
            <div className="consequence-content">
              <div className="consequence-label">Seismic Magnitude</div>
              <div className="consequence-value">
                M{formatNumber(ai_predicted_consequences?.predicted_seismic_magnitude ?? 0, 1)}
              </div>
              <div className="consequence-severity">
                {getSeverityLevel(ai_predicted_consequences?.predicted_seismic_magnitude ?? 0, severityThresholds.seismic).toUpperCase()}
              </div>
            </div>
          </div>

          <div className="consequence-item medium">
            <div className="consequence-icon">💨</div>
            <div className="consequence-content">
              <div className="consequence-label">Blast Radius</div>
              <div className="consequence-value">
                {formatNumber(ai_predicted_consequences?.blast_radius_km ?? 0, 1)} km
              </div>
              <div className="consequence-severity">REGIONAL</div>
            </div>
          </div>

          <div className="consequence-item low">
            <div className="consequence-icon">🕳️</div>
            <div className="consequence-content">
              <div className="consequence-label">Crater Diameter</div>
              <div className="consequence-value">
                {formatNumber(ai_predicted_consequences?.crater_diameter_km ?? 0, 1)} km
              </div>
              <div className="consequence-severity">CONTINENTAL</div>
            </div>
          </div>
        </div>
      </div>

      {/* Deflection Effectiveness */}
      {mission_parameters && (
        <div className="result-section">
          <div className="section-header">
            <Zap size={20} />
            <h3>Deflection Parameters</h3>
          </div>
          <div className="deflection-metrics">
            <div className="metric">
              <div className="metric-label">Lead Time (LTI)</div>
              <div className="metric-value">
                {formatLeadTime(mission_parameters.lti_days)}
              </div>
              <div className="metric-description">
                {mission_parameters.lti_days > 365 
                  ? `Time available for deflection mission`
                  : mission_parameters.lti_days > 0
                  ? 'SHORT TIMELINE - Urgent action required'
                  : 'CRITICAL - Insufficient warning time'}
              </div>
            </div>
            <div className="metric">
              <div className="metric-label">Required ΔV</div>
              <div className="metric-value">{formatNumber(mission_parameters?.required_dv_ms ?? 0, 6)} m/s</div>
              <div className="metric-description">Velocity change needed for safe deflection</div>
            </div>
            <div className="metric">
              <div className="metric-label">Mission Difficulty</div>
              <div className="metric-value">
                {calculateDifficulty(mission_parameters)}
              </div>
              <div className="metric-description">Overall mission complexity assessment</div>
            </div>
          </div>
        </div>
      )}

      {/* AI System Status */}
      <div className="result-section">
        <div className="section-header">
          <CheckCircle size={20} />
          <h3>Analysis Metadata</h3>
        </div>
        <div className="ai-status">
          <div className="status-item">
            <span>AI Model:</span>
            <span className={`status-value ${missionPlan.analysis_metadata?.ai_model_loaded ? 'status-good' : 'status-warning'}`}>
              {missionPlan.analysis_metadata?.ai_model_loaded ? 'LOADED ✅' : 'FALLBACK ⚠️'}
            </span>
          </div>
          <div className="status-item">
            <span>Analysis Type:</span>
            <span className="status-value">{(missionPlan.analysis_metadata?.model_type ?? 'unknown').toUpperCase()}</span>
          </div>
          <div className="status-item">
            <span>System Version:</span>
            <span className="status-value">{missionPlan.analysis_metadata?.version ?? 'Unknown'}</span>
          </div>
          <div className="status-item">
            <span>Data Sources:</span>
            <span className="status-value">
              {missionPlan.asteroid_info?.data_sources?.join(', ') ?? 'Unknown'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;