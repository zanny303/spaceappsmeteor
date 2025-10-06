# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a NASA Space Apps Challenge 2024 project: an AI-enhanced planetary defense system that models asteroid impact scenarios, predicts consequences, and evaluates mitigation strategies using real NASA and USGS datasets.

**Architecture:** Full-stack web application with Python Flask backend and React frontend
- Backend uses real-time data from NASA NEO API, JPL Horizons, JPL Small Body Database, and USGS services
- Frontend provides 3D visualization (Three.js), interactive maps (Leaflet), and AI chat interface
- Physics engine uses poliastro for orbital mechanics and astropy for astronomical calculations
- ML service uses Random Forest model for mission planning recommendations

## Development Commands

### Backend (Python/Flask)

```bash
# From backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (localhost:5000)
python app.py

# Run tests
pytest test_app.py
pytest test_physics_service.py

# Train ML model (if needed)
python train_mission_model.py
```

### Frontend (React)

```bash
# From frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (localhost:3000)
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Running Full Stack

1. Start backend: `cd backend && python app.py` (runs on port 5000)
2. Start frontend: `cd frontend && npm start` (runs on port 3000)
3. Health check: Navigate to http://127.0.0.1:5000/api/health

## Key Architecture Patterns

### Backend Service Layer

The backend follows a service-oriented architecture with dedicated modules:

- **app.py**: Main Flask application with API routes and error handling
  - `/api/full_analysis` - Primary asteroid analysis endpoint
  - `/api/recalculate_trajectory` - Deflection simulation
  - `/api/generate_pdf` - PDF report generation
  - `/api/real_time/*` - Live NASA/USGS data endpoints

- **horizons_service.py**: Fetches asteroid data from JPL Horizons API
- **physics_service.py**: Orbital mechanics calculations using poliastro
  - `calculate_real_trajectory()` - Propagates asteroid orbits
  - `calculate_hazard_corridor()` - Monte Carlo uncertainty modeling
  - `recalculate_trajectory_with_deflection()` - DART-mission-validated physics

- **ml_service.py**: AI/ML predictions using Random Forest model
  - `recommend_mission_plan_with_ai()` - Mission architecture selection
  - `predict_consequences_with_ai()` - Impact consequence prediction
  - Model file: `ml_models/mission_planner_model.pkl`

- **nasa_neows_service.py**: Real-time NEO data from NASA API
- **small_body_service.py**: JPL Small Body Database integration
- **usgs_service.py**: Earthquake and elevation data from USGS
- **report_generator.py**: PDF briefing generation using ReportLab

### Frontend Component Structure

React application with component-based architecture:

- **App.js**: Main application orchestrator with state management
- **components/SolarSystem3D.js**: Three.js 3D solar system visualization
- **components/ImpactMap.js**: Leaflet-based impact zone mapping
- **components/MissionControls.js**: Deflection parameter controls
- **components/ResultsPanel.js**: AI prediction results display
- **components/AIChatPanel.js**: Interactive AI assistant
- **services/api.js**: Backend API integration layer

### Data Flow

1. User selects asteroid → Frontend calls `/api/full_analysis`
2. Backend fetches live data from JPL Horizons
3. Physics service calculates trajectory using poliastro orbital propagation
4. ML service generates mission recommendations using trained Random Forest
5. Results flow back through API → Frontend visualizes in 3D + maps

### Physics Engine Details

**Trajectory Propagation:**
- Uses poliastro `Orbit.from_vectors()` with state vectors [x, y, z, vx, vy, vz]
- Propagates using Keplerian orbital elements
- Optimized to 50 trajectory points (reduced from 250) for performance
- Fallback to analytical propagation if numerical integration fails

**Deflection Modeling:**
- Based on DART mission results (beta factor = 3.6)
- Momentum transfer efficiency = 0.85
- Delta-v calculation accounts for lead time and asteroid mass
- Applies retrograde thrust along velocity vector

**Monte Carlo Uncertainty:**
- Reduced to 8 simulations (from 25) for performance
- Position uncertainty: 150 km std dev
- Velocity uncertainty: 0.025 km/s std dev

### ML Model Training

The mission planner model is trained on scenarios combining:
- Lead Time to Impact (LTI) in days
- Required delta-v in m/s
- Asteroid mass (log10 scale)

Output classes: Launch architecture (Earth/Cislunar) × Interceptor type (Kinetic/Nuclear)

To retrain: `python train_mission_model.py` (creates new `ml_models/mission_planner_model.pkl`)

## External Data Sources

All services integrate real-time data:
- **JPL Horizons**: State vectors and orbital elements (horizons_service.py)
- **NASA NEO API**: Close approach data and diameter estimates (nasa_neows_service.py)
- **JPL Sentry**: Impact probability monitoring (small_body_service.py)
- **USGS Earthquake Catalog**: Historical seismic comparison (usgs_service.py)
- **USGS Elevation API**: Terrain analysis for impact sites (usgs_service.py)

## Important Implementation Notes

### Asteroid ID Format
Valid asteroid IDs: numbers, letters, spaces, hyphens, periods, parentheses (max 100 chars)
Examples: "99942" (Apophis), "101955" (Bennu), "(433) Eros"

### State Vector Format
State vectors are 6-element arrays: `[x, y, z, vx, vy, vz]` in km and km/s

### Performance Optimizations
- Trajectory calculations reduced to 50 points (from 250)
- Monte Carlo simulations reduced to 8 (from 25)
- Propagation days reduced to 180 (from 450) for hazard corridors
- These values can be increased in physics_service.py if performance allows

### Error Handling
Backend uses comprehensive fallbacks:
- If JPL Horizons fails → uses default parameters
- If ML model unavailable → physics-based recommendations
- If trajectory propagation fails → analytical fallback
- All services have try-except with logging

### Rate Limiting
Flask-Limiter configured:
- `/api/full_analysis`: 10/minute
- `/api/recalculate_trajectory`: 20/minute
- `/api/generate_pdf`: 5/minute
- Real-time endpoints: 15-30/minute

## Testing Quick Reference

Famous test asteroids (use these IDs):
- `99942` - Apophis (well-known close approacher)
- `101955` - Bennu (OSIRIS-REx target)
- `25143` - Itokawa (Hayabusa target)
- `433` - Eros
- `2023 DW` - Recent discovery

Health check endpoint shows all service statuses: GET `/api/health`
