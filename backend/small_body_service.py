import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JPLSmallBodyDB:
    def __init__(self):
        # CORRECT JPL Small Body Database URLs
        self.base_url = "https://ssd-api.jpl.nasa.gov/sbdb.api"
        self.sentry_url = "https://ssd-api.jpl.nasa.gov/sentry.api"
        self.cad_url = "https://ssd-api.jpl.nasa.gov/cad.api"  # Close Approach Data
    
    def get_small_body_data(self, asteroid_id):
        """Get detailed orbital data from JPL Small Body Database - CORRECT ENDPOINT"""
        try:
            # CORRECT JPL SBDB query format
            url = f"{self.base_url}"
            params = {
                'sstr': asteroid_id,
                'cov': 'mat',  # Get covariance matrix
                'phys-par': 'true',  # Get physical parameters
                'full-prec': 'true'  # Full precision
            }
            
            logger.info(f"🛰️ Querying JPL Small Body DB for {asteroid_id}")
            logger.info(f"🔗 URL: {url}?sstr={asteroid_id}")
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"❌ JPL SBDB error: {data['error']}")
                return None
                
            logger.info(f"✅ SUCCESS: Retrieved JPL Small Body data for {data.get('object', {}).get('fullname', asteroid_id)}")
            
            return self._process_small_body_data(data)
            
        except Exception as e:
            logger.error(f"❌ JPL Small Body DB query failed: {e}")
            return None
    
    def get_sentry_impact_risks(self):
        """Get real-time impact risks from NASA Sentry system - CORRECT ENDPOINT"""
        try:
            params = {
                'sort': 'ip',  # Sort by impact probability
                'limit': 50,   # Top 50 risks
                'all': '1'     # Get all data
            }
            
            logger.info("⚠️ Fetching REAL-TIME Sentry impact risk data")
            response = requests.get(self.sentry_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"❌ Sentry error: {data['error']}")
                return []
                
            risks = self._process_sentry_data(data)
            logger.info(f"✅ SUCCESS: Retrieved {len(risks)} REAL-TIME impact risks from Sentry")
            return risks
            
        except Exception as e:
            logger.error(f"❌ Sentry impact risk monitoring failed: {e}")
            return []
    
    def get_close_approach_data(self, asteroid_id):
        """Get close approach data from JPL - CORRECT ENDPOINT"""
        try:
            url = f"{self.cad_url}"
            params = {
                'des': asteroid_id,
                'date-min': '1900-01-01',
                'date-max': '2100-01-01',
                'dist-max': '0.2'  # Within 0.2 AU
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Retrieved {len(data.get('data', []))} close approaches")
            return data
            
        except Exception as e:
            logger.error(f"Close approach data failed: {e}")
            return None
    
    def _process_small_body_data(self, data):
        """Process JPL Small Body Database response"""
        if 'error' in data:
            return None
        
        object_data = data.get('object', {})
        orbit_data = data.get('orbit', {})
        physical_data = data.get('physical_parameters', {})
        
        processed = {
            'name': object_data.get('fullname', 'Unknown'),
            'id': object_data.get('spk', 'Unknown'),
            'orbit_class': object_data.get('orbit_class', {}).get('name', 'Unknown'),
            'data_source': 'JPL_Small_Body_Database_Real_Time',
            'api_status': 'ACTIVE'
        }
        
        # Extract comprehensive orbital elements
        if orbit_data:
            processed['orbital_elements'] = {
                'eccentricity': float(orbit_data.get('e', 0)),
                'semi_major_axis_au': float(orbit_data.get('a', 0)),
                'inclination_deg': float(orbit_data.get('i', 0)),
                'ascending_node_deg': float(orbit_data.get('om', 0)),
                'argument_of_perihelion_deg': float(orbit_data.get('w', 0)),
                'mean_anomaly_deg': float(orbit_data.get('ma', 0)),
                'perihelion_distance_au': float(orbit_data.get('q', 0)),
                'aphelion_distance_au': float(orbit_data.get('ad', 0)),
                'orbital_period_days': float(orbit_data.get('per', 0)),
                'first_observation': orbit_data.get('first_obs', 'Unknown'),
                'last_observation': orbit_data.get('last_obs', 'Unknown'),
                'data_arc_days': orbit_data.get('data_arc', 'Unknown'),
                'condition_code': orbit_data.get('condition_code', 'Unknown')
            }
        
        # Extract physical parameters
        if physical_data:
            processed['physical_parameters'] = {
                'diameter_km': physical_data.get('diameter', 'Unknown'),
                'albedo': physical_data.get('albedo', 'Unknown'),
                'spectral_type': physical_data.get('spec_T', 'Unknown'),
                'rotation_period_hours': physical_data.get('rot_per', 'Unknown'),
                'density_kg_m3': physical_data.get('density', 'Unknown')
            }
        
        logger.info(f"📊 Processed JPL data with {len(processed.get('orbital_elements', {}))} orbital elements")
        return processed
    
    def _process_sentry_data(self, data):
        """Process NASA Sentry impact risk data"""
        risks = []
        
        for item in data.get('data', []):
            risk = {
                'object_name': item.get('des', 'Unknown'),
                'impact_probability': float(item.get('ip', 0)),
                'impact_year_range': item.get('range', 'Unknown'),
                'potential_impacts': int(item.get('n_imp', 0)),
                'torino_scale': item.get('ts', '0'),
                'palermo_scale': float(item.get('ps_max', 0)),
                'diameter_km': float(item.get('diameter', 0)),
                'velocity_km_s': float(item.get('v_inf', 0)),
                'energy_mt': float(item.get('energy', 0)),
                'last_observation': item.get('last_obs', 'Unknown'),
                'data_source': 'NASA_Sentry_Real_Time'
            }
            
            # Only include significant risks (above 1 in 10 million probability)
            if risk['impact_probability'] > 1e-7:
                risks.append(risk)
        
        return sorted(risks, key=lambda x: x['impact_probability'], reverse=True)

# Global instance
jpl_smallbody = JPLSmallBodyDB()