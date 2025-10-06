# 🛡️ NASA Planetary Defense System

**AI-Enhanced Asteroid Impact Analysis & Mission Planning Platform**

[![NASA Space Apps Challenge 2024](https://img.shields.io/badge/NASA-Space%20Apps%202024-blue)](https://www.spaceappschallenge.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Real-time asteroid threat analysis using NASA/JPL data, advanced orbital mechanics, and AI-powered mission recommendations.

![System Overview](docs/system-overview.png)

---

## 🌟 Features

### 🔭 **Real-Time NASA Data Integration**
- **NASA NeoWs API**: Live asteroid physical parameters and close approach data
- **JPL Horizons**: High-precision orbital state vectors and ephemeris
- **JPL Small Body Database**: Comprehensive orbital elements for 600,000+ objects
- **USGS Services**: Earthquake comparison data and terrain analysis

### 🤖 **AI-Powered Analysis**
- **RAG Chatbot**: Ask questions about planetary defense using NASA documentation
- **Machine Learning Mission Planner**: Random Forest model trained on deflection scenarios
- **Impact Consequence Prediction**: Physics-based + AI-enhanced damage assessment
- **Smart Recommendations**: Context-aware mission strategy selection

### 🎨 **Interactive 3D Visualization**
- **Solar System View**: Three.js-powered 3D trajectory visualization
- **Hazard Corridor**: Monte Carlo uncertainty modeling (8 trajectories)
- **Deflection Preview**: Real-time simulation of mission outcomes
- **Impact Mapping**: Leaflet-based risk zone visualization

### 🚀 **Mission Planning**
- **Kinetic Impactor** strategies (DART-validated physics)
- **Nuclear Deflection** options for large asteroids
- **Cislunar Depot** vs **Earth-Based Launch** analysis
- **Delta-V calculations** with lead time optimization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/nasa-space-apps-2025.git
cd nasa-space-apps-2025
```

**2. Set up the backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs on **http://localhost:5000**
use curl command to ensure backend runs on this port in the terminal

**3. Set up the frontend:**
```bash
cd frontend
npm install
npm start
```
Frontend runs on **http://localhost:3000**

**4. Access the application:**
Open [http://localhost:3000](http://localhost:3000) in your browser

---

## 💡 How to Use

### 1. **Analyze an Asteroid**
Enter an asteroid ID (e.g., `99942` for Apophis, `101955` for Bennu) and click "Analyze Threat"

### 2. **View the Analysis**
- **3D Visualization**: See orbital trajectories and impact predictions
- **Impact Map**: View potential damage zones
- **AI Recommendations**: Review mission strategies
- **Statistics**: Examine impact energy, seismic effects, casualties

### 3. **Simulate Deflection**
- Adjust lead time, delta-v, and mission parameters
- View updated trajectory in real-time
- Compare before/after scenarios

### 4. **Ask the AI Assistant**
- Click the chat panel
- Ask questions like:
  - "What is the DART mission?"
  - "How is impact energy calculated?"
  - "Explain the Torino Scale"
- Get answers backed by NASA documentation with sources

---

## 🎯 Test Asteroids

Try these well-known Near-Earth Objects:

| ID | Name | Description |
|---|---|---|
| `99942` | Apophis | Famous close-approacher (2029) |
| `101955` | Bennu | OSIRIS-REx mission target |
| `25143` | Itokawa | Hayabusa mission target |
| `433` | Eros | First asteroid orbited by spacecraft |

---

## 🛠️ Technology Stack

### Backend
- **Flask**: REST API framework
- **Poliastro**: Orbital mechanics (v0.17.0)
- **LangChain**: RAG chatbot framework
- **scikit-learn**: Machine learning models
- **astropy/astroquery**: Astronomical calculations

### Frontend
- **React**: UI framework
- **Three.js**: 3D visualization
- **Leaflet**: Interactive maps
- **D3.js**: Data visualization
- **Axios**: API communication

### Data Sources
- NASA NEO Web Service
- JPL Horizons System
- JPL Small Body Database
- USGS Earthquake Catalog
- USGS Elevation API

---

## 📊 System Architecture

```
User Interface (React)
    ↓
API Layer (Flask)
    ↓
┌──────────────────┬──────────────────┬──────────────────┐
│  NASA/JPL APIs   │  Physics Engine  │   AI/ML Models   │
│  - NeoWs         │  - Poliastro     │  - Random Forest │
│  - Horizons      │  - Trajectory    │  - RAG Chatbot   │
│  - Small Body DB │  - Monte Carlo   │  - Consequence   │
│  - USGS          │  - Deflection    │    Prediction    │
└──────────────────┴──────────────────┴──────────────────┘
    ↓
Visualization & User Feedback
```

---

## 🤝 Contributing

We welcome contributions! Please see [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) for development guidelines.

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NASA**: For providing open APIs and planetary defense data
- **JPL**: For Horizons system and small body database
- **USGS**: For earthquake and elevation data
- **Space Apps Challenge**: For inspiring this project
- **DART Mission Team**: For demonstrating kinetic impact technology

---

## 📞 Contact

**Project Team**: NASA Space Apps 2024
**Email**: team@nasa-planetary-defense.space
**GitHub**: [https://github.com/yourusername/nasa-space-apps-2025]https://github.com/zanny303/spaceappsmeteor

---

## 🌟 Screenshots

### Main Dashboard
![Dashboard](docs/dashboard.png)

### 3D Trajectory Visualization
![3D View](docs/3d-view.png)

### AI Chat Assistant
![Chat Bot](docs/chatbot.png)

### Impact Analysis
![Impact Map](docs/impact-map.png)

---

<div align="center">

**Built with ❤️ for Planetary Defense**

[Report Bug](https://github.com/yourusername/nasa-space-apps-2025/issues) · [Request Feature](https://github.com/yourusername/nasa-space-apps-2025/issues) · [Documentation](TECHNICAL_DOCUMENTATION.md)

</div>


