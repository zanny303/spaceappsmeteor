# backend/usgs_service.py
import requests
import logging
from datetime import datetime, timedelta
import math # BUG FIX: Added math import for log10

logger = logging.getLogger(__name__)

class USGSDataService:
    def __init__(self):
        self.earthquake_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        self.elevation_url = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/export"
    
    def get_earthquake_comparison(self, impact_energy_megatons):
        """Get real earthquakes for comparison with impact energy"""
        try:
            # Calculate equivalent seismic magnitude
            equivalent_magnitude = self._energy_to_magnitude(impact_energy_megatons)

            # Get recent large earthquakes for comparison
            params = {
                'format': 'geojson',
                'starttime': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                'minmagnitude': max(4.5, equivalent_magnitude - 2),  # Get slightly smaller quakes for context
                'limit': 10,
                'orderby': 'magnitude'
            }

            logger.info(f"🌍 Querying USGS for earthquakes >= M{params['minmagnitude']:.1f}")
            response = requests.get(self.earthquake_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            result = self._process_earthquake_comparison(data, equivalent_magnitude, impact_energy_megatons)

            if result:
                logger.info(f"✅ Retrieved {len(result['comparable_earthquakes'])} comparable earthquakes")

            return result

        except Exception as e:
            logger.error(f"USGS earthquake data failed: {e}")
            return None

    def get_recent_significant_earthquakes(self, days=30, min_magnitude=6.0):
        """Get recent significant earthquakes for context"""
        try:
            params = {
                'format': 'geojson',
                'starttime': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'minmagnitude': min_magnitude,
                'orderby': 'time-asc'
            }

            logger.info(f"🌍 Fetching earthquakes from last {days} days, M>={min_magnitude}")
            response = requests.get(self.earthquake_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            earthquakes = []

            for feature in data.get('features', []):
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [0, 0, 0])

                earthquakes.append({
                    'magnitude': props.get('mag', 0),
                    'location': props.get('place', 'Unknown'),
                    'time': datetime.fromtimestamp(props.get('time', 0) / 1000).isoformat(),
                    'latitude': coords[1] if len(coords) > 1 else 0,
                    'longitude': coords[0] if len(coords) > 0 else 0,
                    'depth_km': coords[2] if len(coords) > 2 else 0,
                    'url': props.get('url', ''),
                    'tsunami': props.get('tsunami', 0) == 1
                })

            logger.info(f"✅ Retrieved {len(earthquakes)} recent significant earthquakes")
            return earthquakes

        except Exception as e:
            logger.error(f"Recent earthquakes query failed: {e}")
            return []
    
    def get_elevation_profile(self, lat, lng, radius_km=100):
        """Get elevation data for impact site analysis using USGS API"""
        try:
            # Get elevation for center point using USGS Elevation Point Query Service
            center_elevation = self._get_point_elevation(lat, lng)

            # Sample points in a circle around the impact site
            sample_points = 8  # 8 directions
            elevations = [center_elevation] if center_elevation is not None else []

            for i in range(sample_points):
                angle = 2 * math.pi * i / sample_points
                # Calculate point at radius_km distance
                # Rough approximation: 1 degree ≈ 111 km
                sample_lat = lat + (radius_km / 111) * math.cos(angle)
                sample_lng = lng + (radius_km / 111) * math.sin(angle) / math.cos(math.radians(lat))

                elev = self._get_point_elevation(sample_lat, sample_lng)
                if elev is not None:
                    elevations.append(elev)

            if not elevations:
                logger.warning(f"No elevation data retrieved, using mock data")
                return self._generate_mock_elevation_profile(lat, lng, radius_km)

            # Calculate statistics
            max_elev = max(elevations)
            min_elev = min(elevations)
            avg_elev = sum(elevations) / len(elevations)

            # Determine coastal proximity (simplified: elevation < 100m suggests coastal)
            is_coastal = min_elev < 100 and abs(lat) < 70

            logger.info(f"✅ Retrieved USGS elevation data: {len(elevations)} points, range {min_elev:.1f}-{max_elev:.1f}m")

            return {
                'center': {'lat': lat, 'lng': lng},
                'radius_km': radius_km,
                'max_elevation_m': round(max_elev, 1),
                'min_elevation_m': round(min_elev, 1),
                'avg_elevation_m': round(avg_elev, 1),
                'sample_count': len(elevations),
                'coastal_distance_km': self._estimate_coastal_distance(min_elev, avg_elev),
                'tsunami_risk': self._assess_tsunami_risk(min_elev, avg_elev, lat),
                'data_source': 'USGS_Elevation_API'
            }

        except Exception as e:
            logger.error(f"Elevation data failed: {e}")
            return self._generate_mock_elevation_profile(lat, lng, radius_km)

    def _get_point_elevation(self, lat, lng):
        """Get elevation for a single point using USGS Elevation Point Query Service"""
        try:
            # USGS Elevation Point Query Service (EPQS)
            url = "https://epqs.nationalmap.gov/v1/json"
            params = {
                'x': lng,
                'y': lat,
                'units': 'Meters',
                'output': 'json'
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            elevation = data.get('value')

            if elevation is not None:
                return float(elevation)
            return None

        except Exception as e:
            logger.debug(f"Point elevation query failed for ({lat}, {lng}): {e}")
            return None
    
    def _energy_to_magnitude(self, energy_megatons):
        """Convert impact energy to equivalent seismic magnitude"""
        # Richter scale formula for energy comparison
        # M = (2/3) * log10(E) - 2.9 where E is in joules
        energy_joules = energy_megatons * 4.184e15
        # BUG FIX: Changed energy_joules.log10() to math.log10(energy_joules)
        return (2/3) * (math.log10(energy_joules)) - 2.9 if energy_joules > 0 else 0
    
    def _process_earthquake_comparison(self, data, equivalent_magnitude, impact_energy):
        """Process earthquake data for impact comparison"""
        comparison = {
            'impact_energy_megatons': impact_energy,
            'equivalent_seismic_magnitude': round(equivalent_magnitude, 1),
            'comparable_earthquakes': [],
            'largest_historical': {
                'magnitude': 9.5,  # Chile 1960
                'location': 'Valdivia, Chile',
                'year': 1960,
                'energy_megatons': 2500  # Approximate
            }
        }
        
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            quake = {
                'magnitude': props.get('mag', 0),
                'location': props.get('place', 'Unknown'),
                'time': datetime.fromtimestamp(props.get('time', 0) / 1000).isoformat(),
                'depth_km': feature.get('geometry', {}).get('coordinates', [0,0,0])[2],
                'significance': props.get('sig', 0)
            }
            comparison['comparable_earthquakes'].append(quake)
        
        return comparison
    
    def _generate_mock_elevation_profile(self, lat, lng, radius_km):
        """Generate realistic elevation profile (mock for demo)"""
        # In production, integrate with USGS National Map Elevation API
        return {
            'center': {'lat': lat, 'lng': lng},
            'radius_km': radius_km,
            'max_elevation_m': 850,
            'min_elevation_m': -120,
            'avg_elevation_m': 240,
            'coastal_distance_km': 45,
            'tsunami_risk': 'MEDIUM' if self._is_coastal(lat, lng) else 'LOW'
        }
    
    def _is_coastal(self, lat, lng):
        """Simple coastal detection (mock)"""
        # Simplified - real implementation would use coastline data
        return abs(lat) < 60 and (abs(lng) < 100)  # Rough approximation

    def _estimate_coastal_distance(self, min_elevation, avg_elevation):
        """Estimate distance to coast based on elevation profile"""
        if min_elevation < 10:
            return 0  # Very close to coast or below sea level
        elif min_elevation < 50:
            return 25  # Likely within 25km of coast
        elif min_elevation < 100:
            return 50  # Possibly within 50km
        else:
            return 100  # Likely inland

    def _assess_tsunami_risk(self, min_elevation, avg_elevation, lat):
        """Assess tsunami risk based on elevation and location"""
        # Polar regions have lower tsunami risk
        if abs(lat) > 70:
            return 'LOW'

        # Elevation-based assessment
        if min_elevation < 10:
            return 'CRITICAL'
        elif min_elevation < 30:
            return 'HIGH'
        elif min_elevation < 100:
            return 'MEDIUM'
        else:
            return 'LOW'

# Global instance
usgs_service = USGSDataService()