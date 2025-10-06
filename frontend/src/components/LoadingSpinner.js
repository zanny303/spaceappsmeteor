// src/components/LoadingSpinner.js
import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="loading-spinner">
      <div className="spinner-content">
        <div className="spinner"></div>
        <h3>🚀Planetary Defense AI</h3>
        <p>Processing asteroid threat assessment...</p>
        <div className="loading-details">
          <div className="loading-step">🛰️ Querying orbital data</div>
          <div className="loading-step">🤖 Running AI analysis</div>
          <div className="loading-step">📊 Calculating impact consequences</div>
          <div className="loading-step">🎯 Generating mission recommendations</div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;