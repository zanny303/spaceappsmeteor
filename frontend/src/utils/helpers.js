// src/utils/helpers.js

// Format large numbers with appropriate units
export const formatNumber = (num) => {
  if (num >= 1e12) {
    return (num / 1e12).toFixed(2) + 'T';
  }
  if (num >= 1e9) {
    return (num / 1e9).toFixed(2) + 'B';
  }
  if (num >= 1e6) {
    return (num / 1e6).toFixed(2) + 'M';
  }
  if (num >= 1e3) {
    return (num / 1e3).toFixed(2) + 'K';
  }
  return num.toString();
};

// Calculate mission difficulty based on parameters
export const calculateMissionDifficulty = (ltiDays, deltaV, mass) => {
  let score = 0;
  
  // Time factor (shorter time = harder)
  if (ltiDays < 180) score += 3;
  else if (ltiDays < 365) score += 2;
  else if (ltiDays < 730) score += 1;
  
  // Delta-V factor (higher delta-v = harder)
  if (deltaV > 0.02) score += 3;
  else if (deltaV > 0.01) score += 2;
  else if (deltaV > 0.005) score += 1;
  
  // Mass factor (larger mass = harder)
  if (mass > 1e12) score += 3;
  else if (mass > 1e11) score += 2;
  else if (mass > 1e10) score += 1;
  
  if (score >= 6) return 'VERY HIGH';
  if (score >= 4) return 'HIGH';
  if (score >= 2) return 'MEDIUM';
  return 'LOW';
};

// Generate color based on severity
export const getSeverityColor = (severity) => {
  const colors = {
    critical: '#ff4444',
    high: '#ff6b6b',
    medium: '#feca57',
    low: '#48dbfb'
  };
  return colors[severity] || '#666';
};

// Debounce function for performance
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Validate asteroid ID format
export const isValidAsteroidId = (id) => {
  return /^\d+$/.test(id) && id.length > 0 && id.length <= 20;
};

// Export mission data as JSON
export const exportMissionData = (missionPlan) => {
  const dataStr = JSON.stringify(missionPlan, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  return URL.createObjectURL(dataBlob);
};

// Format date for display
export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};