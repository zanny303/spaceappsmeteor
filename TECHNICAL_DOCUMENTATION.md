# 🔬 Technical Documentation

**NASA Planetary Defense System - Developer Guide**

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Backend Services](#backend-services)
3. [Frontend Components](#frontend-components)
4. [Data Flow](#data-flow)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [Deployment](#deployment)
8. [Testing](#testing)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  - App.js: Main orchestrator                                │
│  - SolarSystem3D.js: Three.js visualization                 │
│  - ImpactMap.js: Leaflet mapping                           │
│  - AIChatPanel.js: RAG chatbot UI                          │
│  - MissionControls.js: Parameter inputs                     │
│  - ResultsPanel.js: Analysis display                       │
└─────────────────────────────────────────────────────────────┘
                              ↓↑ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (Flask)                        │
│  - app.py: REST endpoints                                   │
│  - Rate limiting (Flask-Limiter)                            │
│  - CORS enabled (Flask-CORS)                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬──────────────────────┐
│   Data Services  │  Physics Engine  │    AI/ML Services    │
├──────────────────┼──────────────────┼──────────────────────┤
│ nasa_neows_      │ physics_service  │ ml_service.py        │
│  service.py      │  .py             │ - Random Forest      │
│                  │ - Poliastro      │ - Consequence AI     │
│ horizons_        │ - Trajectory     │                      │
│  service.py      │   Propagation    │ rag_chat_service.py  │
│                  │ - Monte Carlo    │ - LangChain          │
│ small_body_      │                  │ - Document Store     │
│  service.py      │                  │ - Knowledge Base     │
│                  │                  │                      │
│ usgs_service.py  │                  │                      │
│ - Earthquakes    │                  │                      │
│ - Elevation      │                  │                      │
└──────────────────┴──────────────────┴──────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    External APIs                             │
│  - NASA NeoWs API                                            │
│  - JPL Horizons System                                       │
│  - JPL Small Body Database                                   │
│  - USGS Earthquake Catalog                                   │
│  - USGS Elevation Point Query Service                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Services

### 1. NASA Data Services

#### nasa_neows_service.py
**Purpose**: Fetch asteroid physical data from NASA Near-Earth Object Web Service

**Key Functions**:
```python
def get_neo_details(asteroid_id: str) -> dict:
    """
    Retrieves asteroid data with smart ID mapping.
    Maps simple IDs (99942) to NASA format (2099942).

    Returns:
        {
            'name': str,
            'estimated_diameter': {...},
            'close_approach_data': [...],
            'threat_metrics': {
                'threat_score': float,
                'torino_scale': int,
                'palermo_scale': float
            }
        }
    """
```

**API Endpoint**: `https://api.nasa.gov/neo/rest/v1/neo/{id}`

**Known ID Mappings**:
- `99942` → `2099942` (Apophis)
- `101955` → `2101955` (Bennu)
- `25143` → `2025143` (Itokawa)
- `433` → `2000433` (Eros)

#### horizons_service.py
**Purpose**: High-precision orbital data from JPL Horizons

**Critical Unit Conversions**:
```python
AU_TO_KM = 1.496e8        # 1 AU = 149.6 million km
DAY_TO_SEC = 86400.0      # 1 day = 86400 seconds

# Positions: AU → km
state_vector[0:3] *= AU_TO_KM

# Velocities: AU/day → km/s
state_vector[3:6] *= AU_TO_KM / DAY_TO_SEC
```

**State Vector Format**: `[x, y, z, vx, vy, vz]` in km and km/s

#### usgs_service.py
**Purpose**: Earthquake comparison and terrain analysis

**Endpoints Used**:
- Earthquake API: `https://earthquake.usgs.gov/fdsnws/event/1/query`
- Elevation API: `https://epqs.nationalmap.gov/v1/json`

**Key Formulas**:
```python
# Richter magnitude from energy
def _energy_to_magnitude(energy_megatons):
    energy_joules = energy_megatons * 4.184e15
    return (2/3) * log10(energy_joules) - 2.9

# Tsunami risk assessment
def _assess_tsunami_risk(min_elevation, avg_elevation, lat):
    if min_elevation < 10: return 'CRITICAL'
    if min_elevation < 30: return 'HIGH'
    if min_elevation < 100: return 'MEDIUM'
    return 'LOW'
```

---

### 2. Physics Engine

#### physics_service.py
**Purpose**: Orbital mechanics and trajectory calculations using Poliastro

**Trajectory Propagation**:
```python
from poliastro.twobody import Orbit
from poliastro.bodies import Sun

def calculate_real_trajectory(state_vector, propagation_days=365):
    # Convert to astropy units
    r_vec = state_vector[:3] * u.km
    v_vec = state_vector[3:] * u.km / u.s

    # Create orbit object
    orbit = Orbit.from_vectors(Sun, r_vec, v_vec)

    # Propagate over time
    time_range = np.linspace(0, propagation_days, 50) * u.day

    for time_offset in time_range:
        propagated_orbit = orbit.propagate(time_offset)
        # Extract position
        position = propagated_orbit.r.to(u.km).value
```

**Monte Carlo Uncertainty**:
- 8 perturbed trajectories
- Position uncertainty: σ = 150 km
- Velocity uncertainty: σ = 0.025 km/s

**Deflection Physics** (DART-validated):
```python
# Momentum transfer efficiency
BETA_FACTOR = 3.6          # From DART mission
EFFICIENCY = 0.85          # Momentum coupling

# Delta-v calculation
def calculate_required_delta_v(mass_kg, lti_days):
    dv = (1e-3 / lti_days) * (1e12 / mass_kg) ** 0.5
    return max(0.0001, min(0.1, dv))  # Constrain to realistic range
```

---

### 3. AI/ML Services

#### ml_service.py
**Purpose**: Mission recommendation and consequence prediction

**Random Forest Model**:
```python
Input Features:
- lti_days: Lead time to impact (days)
- delta_v: Required velocity change (m/s)
- log10(mass): Asteroid mass (log scale)

Output Classes:
- 'Earth-Vehicle_Rapid-Kinetic'
- 'Earth-Vehicle_Heavy-Kinetic'
- 'Earth-Vehicle_Nuclear-Disruption'
- 'Cislunar-Depot_Enhanced-Kinetic'
- 'Cislunar-Depot_Nuclear-Deflection'
```

**Model Location**: `backend/ml_models/mission_planner_model.pkl`

**Training Data**: Synthetic scenarios based on physics constraints

#### rag_chat_service.py
**Purpose**: Retrieval-Augmented Generation chatbot

**Knowledge Base Topics**:
1. Near-Earth Objects (NEOs)
2. DART Mission results
3. Torino Impact Hazard Scale
4. Impact energy calculations
5. Deflection strategies
6. Orbital mechanics
7. Seismic effects
8. Asteroid composition

**Document Retrieval**:
```python
# Simple keyword search (fallback)
def _simple_keyword_search(query, k=3):
    # Score documents by keyword matches
    # Return top-k documents

# Vector search (optional, requires sentence-transformers)
def retrieve_context(query, k=3):
    if vectorstore:
        return vectorstore.similarity_search(query, k)
    else:
        return _simple_keyword_search(query, k)
```

---

## 🎨 Frontend Components

### Component Architecture

```
App.js (State Management)
  ├── SolarSystem3D.js (Three.js)
  │   ├── Scene setup
  │   ├── Orbit creation (Sun, Earth)
  │   ├── Trajectory plotting
  │   └── Camera controls
  │
  ├── ImpactMap.js (Leaflet + D3)
  │   ├── World map projection
  │   ├── Impact zone circles
  │   └── Risk visualization
  │
  ├── AIChatPanel.js (RAG Interface)
  │   ├── Message handling
  │   ├── API integration
  │   ├── Source display
  │   └── Confidence indicators
  │
  ├── MissionControls.js
  │   └── Parameter inputs
  │
  └── ResultsPanel.js
      └── Analysis display
```

### Key Implementation Details

#### SolarSystem3D.js
**Scale Factor**: `SCALE = 1e6` (1 million km per visualization unit)

```javascript
// Correct scaling
const SCALE = 1e6;  // 1M km per unit
// Earth at 150M km = 150 units (1 AU)
earth.position.set(150, 0, 0);

// Plot trajectories
trajectory.map(coord =>
  new THREE.Vector3(
    coord[0] / SCALE,  // km → units
    coord[1] / SCALE,
    coord[2] / SCALE
  )
)
```

#### AIChatPanel.js
**RAG Integration**:
```javascript
const handleSendMessage = async () => {
  const response = await sendChatMessage(message, missionPlan);

  // Response includes:
  // - answer: string
  // - confidence: 'high' | 'medium' | 'low'
  // - sources: [{title, snippet}]
  // - mission_context: string (if available)
}
```

---

## 📡 API Reference

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Full Analysis
```http
POST /api/full_analysis
Content-Type: application/json

Request:
{
  "asteroid_id": "99942"
}

Response:
{
  "asteroid_info": {
    "name": "99942 Apophis (2004 MN4)",
    "diameter_m": 653.9,
    "velocity_kms": 14.16,
    "mass_kg": 3.98e11,
    "data_sources": ["NASA_NEO_WS", "JPL_Horizons"],
    "data_integrity": 100
  },
  "initial_state_vector": [x, y, z, vx, vy, vz],
  "visualization_data": {
    "hazard_corridor": [
      [[x1, y1, z1], [x2, y2, z2], ...]  // 8 trajectories
    ]
  },
  "ai_predicted_consequences": {
    "impact_energy_megatons": 9539.5,
    "blast_radius_km": 22.96,
    "predicted_seismic_magnitude": 7.39,
    "predicted_casualties": 1500000,
    "economic_damage_usd": 8.5e12
  },
  "mission_recommendation": {
    "source": "Cislunar Depot",
    "interceptor_type": "Enhanced Kinetic Impactor",
    "confidence_score": 91.5,
    "rationale": "...",
    "model_type": "random_forest"
  },
  "usgs_data": {
    "earthquake_comparison": {...},
    "elevation_profile": {...}
  }
}
```

#### 2. RAG Chat
```http
POST /api/chat
Content-Type: application/json

Request:
{
  "message": "What is the DART mission?",
  "mission_context": {
    "asteroid_info": {
      "name": "Apophis",
      "diameter_m": 370
    }
  }
}

Response:
{
  "answer": "The DART mission successfully altered...",
  "confidence": "high",
  "sources": [
    {
      "title": "DART Mission",
      "source": "NASA Documentation",
      "snippet": "The DART mission..."
    }
  ],
  "mission_context": "Current Analysis: Apophis | Diameter: 370m"
}
```

#### 3. Trajectory Recalculation
```http
POST /api/recalculate_trajectory
Content-Type: application/json

Request:
{
  "state_vector": [x, y, z, vx, vy, vz],
  "delta_v": 0.001,
  "lead_time_days": 1825
}

Response:
{
  "safe_trajectory": [[x1, y1, z1], ...],
  "deflection_success": true,
  "new_miss_distance_km": 500000
}
```

#### 4. Health Check
```http
GET /api/health

Response:
{
  "status": "operational",
  "services": {
    "nasa_neows": "operational",
    "horizons_service": "operational",
    "usgs_service": "operational",
    "ml_service": "operational",
    "rag_chat": "operational"
  },
  "timestamp": "2024-10-05T17:00:00Z"
}
```

### Rate Limits
- `/api/full_analysis`: 10 requests/minute
- `/api/recalculate_trajectory`: 20 requests/minute
- `/api/chat`: 20 requests/minute
- `/api/health`: 30 requests/minute

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest test_app.py
pytest test_physics_service.py
```

### Test Cases
```python
def test_full_analysis():
    """Test complete asteroid analysis pipeline"""
    response = client.post('/api/full_analysis',
                          json={'asteroid_id': '99942'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'NASA_NEO_WS' in data['asteroid_info']['data_sources']
    assert data['asteroid_info']['data_integrity'] == 100

def test_rag_chat():
    """Test RAG chatbot with NASA docs"""
    response = client.post('/api/chat',
                          json={'message': 'What is DART?'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'confidence' in data
    assert len(data['sources']) > 0
```

### Frontend Testing
```bash
cd frontend
npm test
```

---

## ⚡ Performance Optimization

### Backend Optimizations

**1. Trajectory Resolution Reduced**:
```python
num_points = 50      # Down from 250 (80% reduction)
num_simulations = 8  # Down from 25 (68% reduction)
propagation_days = 180  # Down from 450
```

**2. Caching Strategy**:
```python
# LRU cache for expensive computations
from functools import lru_cache

@lru_cache(maxsize=100)
def calculate_asteroid_mass(diameter, spectral_type='S'):
    # Cached mass calculations
```

**3. Async Tasks** (Future):
```python
# Use Celery for long-running tasks
from celery import Celery

@celery.task
def async_trajectory_calculation(state_vector):
    # Background processing
```

### Frontend Optimizations

**1. React.memo for Components**:
```javascript
export default React.memo(SolarSystem3D, (prevProps, nextProps) => {
  return prevProps.missionPlan === nextProps.missionPlan;
});
```

**2. Debounced API Calls**:
```javascript
const debouncedAnalysis = useDebounce(asteroidId, 500);
```

**3. Three.js Performance**:
```javascript
// Reduce polygon count
const asteroidGeometry = new THREE.SphereGeometry(2, 16, 16);  // Not 32, 32

// Dispose unused objects
renderer.dispose();
geometry.dispose();
material.dispose();
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "NASA API 404 Error"
**Cause**: Asteroid ID not in NASA database
**Solution**: Use ID mapping or try browse endpoint

```python
# Known mappings in nasa_neows_service.py
known_mappings = {
    '99942': '2099942',  # Apophis
    '101955': '2101955',  # Bennu
}
```

#### 2. "State Vector in Wrong Units"
**Cause**: JPL Horizons returns AU, not km
**Solution**: Ensure conversion in horizons_service.py

```python
# MUST multiply by AU_TO_KM (1.496e8)
state_vector[0:3] *= AU_TO_KM
```

#### 3. "Visualization Shows No Trajectories"
**Cause**: Incorrect scale factor
**Solution**: Use SCALE = 1e6 in SolarSystem3D.js

```javascript
const SCALE = 1e6;  // NOT 100000
```

#### 4. "RAG Chat Returns Empty Sources"
**Cause**: LangChain dependencies missing
**Solution**: System automatically falls back to keyword search

```bash
# Optional: Install full dependencies
pip install sentence-transformers transformers
```

#### 5. "CORS Error"
**Cause**: Frontend/backend on different ports
**Solution**: Ensure Flask-CORS is enabled

```python
from flask_cors import CORS
CORS(app)
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in app.py
- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates
- [ ] Configure environment variables
- [ ] Enable logging to files
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure backups
- [ ] Scale with load balancer
- [ ] Use Redis for caching

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 📚 Additional Resources

- [CLAUDE.md](CLAUDE.md) - Claude Code guidance
- [Poliastro Documentation](https://docs.poliastro.space/)
- [NASA APIs](https://api.nasa.gov/)
- [JPL Horizons Manual](https://ssd.jpl.nasa.gov/horizons/manual.html)
- [LangChain Docs](https://python.langchain.com/)

---

<div align="center">

**For questions or support, please open an issue on GitHub**

[Back to README](README.md) | [Report Issue](https://github.com/yourusername/nasa-space-apps-2025/issues)

</div>
