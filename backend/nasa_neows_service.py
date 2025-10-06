import requests
import os
import logging
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class NASANEOData:
    def __init__(self):
        self.api_key = "aAfCOm9YEZ0Gn3lmrotxuQBX13sNCZ0aJMZBgeKW"
        self.base_url = 'https://api.nasa.gov/neo/rest/v1'
        self.session = requests.Session()
    
    def get_neo_details(self, asteroid_id):
        """Get detailed real-time data for specific asteroid from NASA NEO WS"""
        try:
            # NASA NeoWs uses SPK-ID or designation for lookup
            url = f"{self.base_url}/neo/{asteroid_id}"
            params = {'api_key': self.api_key}

            logger.info(f"🛰️ Fetching real-time data for asteroid {asteroid_id} from NASA NEO WS")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            logger.info(f"✅ Retrieved real-time data for {data.get('name', asteroid_id)}")

            return self._enhance_neo_data(data)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"⚠️ Asteroid {asteroid_id} not found in NASA NEO WS, trying browse endpoint")
                # Try browse endpoint as fallback
                return self._try_browse_lookup(asteroid_id)
            else:
                logger.error(f"❌ NASA NEO WS HTTP error for {asteroid_id}: {e}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ NASA NEO WS request failed for {asteroid_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching NEO data: {e}")
            return None

    def _try_browse_lookup(self, asteroid_id):
        """Fallback: Try to find asteroid in browse endpoint with pagination"""
        try:
            # Known mappings for common asteroids
            known_mappings = {
                '99942': '2099942',  # Apophis
                '101955': '2101955',  # Bennu
                '25143': '2025143',   # Itokawa
                '433': '2000433',     # Eros
            }

            # Try known mapping first
            if asteroid_id in known_mappings:
                mapped_id = known_mappings[asteroid_id]
                logger.info(f"Using known ID mapping: {asteroid_id} → {mapped_id}")
                return self.get_neo_details(mapped_id)

            # If asteroid_id is a number without leading '2', try adding it
            if asteroid_id.isdigit() and not asteroid_id.startswith('2'):
                try_id = '2' + asteroid_id.zfill(6)
                logger.info(f"Trying formatted ID: {try_id}")
                response = self.session.get(
                    f"{self.base_url}/neo/{try_id}",
                    params={'api_key': self.api_key},
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Found via formatted ID: {data.get('name')}")
                    return self._enhance_neo_data(data)

            # Search through browse endpoint
            url = f"{self.base_url}/neo/browse"
            params = {'api_key': self.api_key, 'page': 0, 'size': 20}

            for page in range(3):  # Check first 3 pages (60 objects)
                params['page'] = page
                response = self.session.get(url, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()
                neos = data.get('near_earth_objects', [])

                # Search for matching asteroid by ID, name, or designation
                for neo in neos:
                    neo_id = str(neo.get('id', ''))
                    neo_name = neo.get('name', '').upper()
                    neo_designation = neo.get('designation', '').upper()

                    search_id = str(asteroid_id).upper()

                    if (neo_id.endswith(asteroid_id) or
                        search_id in neo_name or
                        search_id in neo_designation or
                        asteroid_id in neo_id):
                        logger.info(f"✅ Found {neo.get('name')} via browse (page {page})")
                        return self._enhance_neo_data(neo)

            logger.warning(f"Asteroid {asteroid_id} not found in browse results")
            return None

        except Exception as e:
            logger.error(f"Browse lookup failed: {e}")
            return None
    
    def get_neo_feed(self, days=7):
        """Get real-time NEO feed for upcoming days"""
        try:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/feed"
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'api_key': self.api_key
            }
            
            logger.info(f"📡 Fetching NEO feed from {start_date} to {end_date}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Retrieved {data.get('element_count', 0)} NEOs in real-time")
            
            return self._process_neo_feed(data)
            
        except Exception as e:
            logger.error(f"❌ NEO feed failed: {e}")
            return {'error': str(e), 'data': []}
    
    def get_close_approach_data(self, asteroid_id):
        """Get real-time close approach data - included in main NEO details"""
        try:
            # Close approach data is included in the main NEO details response
            neo_details = self.get_neo_details(asteroid_id)
            if neo_details and 'close_approach_data' in neo_details:
                return neo_details['close_approach_data']
            return None

        except Exception as e:
            logger.error(f"Close approach data failed: {e}")
            return None
    
    def _enhance_neo_data(self, data):
        """Enhance NASA NEO data with calculated threat metrics"""
        enhanced = data.copy()
        
        # Calculate threat score based on NASA's criteria
        diameter = self._get_average_diameter(data)
        velocity = self._get_approach_velocity(data)
        miss_distance = self._get_miss_distance(data)
        
        enhanced['threat_metrics'] = {
            'threat_score': self._calculate_threat_score(diameter, velocity, miss_distance),
            'impact_probability': self._estimate_impact_probability(miss_distance),
            'energy_equivalent_megatons': self._calculate_impact_energy(diameter, velocity),
            'torino_scale': self._calculate_torino_scale(diameter, miss_distance),
            'palermo_scale': self._calculate_palermo_scale(diameter, velocity, miss_distance)
        }
        
        # Add data source info
        enhanced['data_source'] = 'NASA_NEO_Web_Service_Real_Time'
        enhanced['last_updated'] = datetime.now().isoformat()
        
        return enhanced
    
    def _get_average_diameter(self, data):
        """Calculate average diameter from min/max estimates"""
        try:
            meters = data.get('estimated_diameter', {}).get('meters', {})
            min_diam = meters.get('estimated_diameter_min', 0)
            max_diam = meters.get('estimated_diameter_max', 0)
            return (min_diam + max_diam) / 2
        except:
            return 500.0  # Reasonable fallback
    
    def _get_approach_velocity(self, data):
        """Extract approach velocity from close approach data"""
        try:
            approaches = data.get('close_approach_data', [])
            if approaches:
                return float(approaches[0]['relative_velocity']['kilometers_per_second'])
            return 10.0  # Reasonable fallback in km/s
        except:
            return 10.0
    
    def _get_miss_distance(self, data):
        """Extract miss distance from close approach data"""
        try:
            approaches = data.get('close_approach_data', [])
            if approaches:
                return float(approaches[0]['miss_distance']['kilometers'])
            return 1000000.0  # Reasonable fallback in km
        except:
            return 1000000.0
    
    def _calculate_threat_score(self, diameter, velocity, miss_distance):
        """NASA-inspired threat scoring (0-100 scale)"""
        # Energy component (diameter^3 * velocity^2)
        energy_factor = (diameter ** 3) * (velocity ** 2) / 1e12
        
        # Proximity component (closer = more dangerous)
        proximity_factor = max(0, 1 - (miss_distance / 1e7))
        
        # Combined score
        score = min(100, energy_factor * 10 + proximity_factor * 50)
        return round(score, 1)
    
    def _estimate_impact_probability(self, miss_distance):
        """Estimate impact probability based on miss distance"""
        if miss_distance < 10000:  # Within 10,000 km
            return min(0.1, 10000 / miss_distance / 1000)
        return 0.0001  # Very low probability for distant approaches
    
    def _calculate_impact_energy(self, diameter, velocity):
        """Calculate impact energy in megatons of TNT"""
        volume = (4/3) * math.pi * ((diameter/2) ** 3)
        mass = volume * 2700  # kg, assume density 2700 kg/m³
        energy_joules = 0.5 * mass * (velocity * 1000) ** 2
        return energy_joules / (4.184e15)  # Convert to megatons TNT
    
    def _calculate_torino_scale(self, diameter, miss_distance):
        """Calculate Torino Impact Hazard Scale (0-10)"""
        energy = self._calculate_impact_energy(diameter, 20)  # Use typical velocity
        
        if miss_distance > 1000000:  # Very safe
            return 0
        elif energy < 1:  # 1 megaton threshold
            return 1 if miss_distance < 100000 else 0
        elif energy < 10:
            return 2 if miss_distance < 50000 else 1
        else:
            return min(10, int(energy / 10) + 2)
    
    def _calculate_palermo_scale(self, diameter, velocity, miss_distance):
        """Calculate Palermo Technical Impact Hazard Scale"""
        # Simplified calculation for demonstration
        energy = self._calculate_impact_energy(diameter, velocity)
        background_risk = 1e-8  # Simplified background risk
        
        if energy < 1 or miss_distance > 1000000:
            return -10  # Very low risk
        
        risk_ratio = (1 / miss_distance * 1e6) * energy / 100
        return round(math.log10(risk_ratio / background_risk), 2)
    
    def _process_neo_feed(self, data):
        """Process and enhance raw NEO feed data"""
        processed = {
            'element_count': data.get('element_count', 0),
            'near_earth_objects': {},
            'potential_hazards': [],
            'last_updated': datetime.now().isoformat(),
            'data_source': 'NASA_NEO_WS_Real_Time_Feed'
        }
        
        for date_str, neos in data.get('near_earth_objects', {}).items():
            processed['near_earth_objects'][date_str] = []
            
            for neo in neos:
                enhanced_neo = self._enhance_neo_data(neo)
                processed['near_earth_objects'][date_str].append(enhanced_neo)
                
                # Track potentially hazardous objects
                if enhanced_neo.get('is_potentially_hazardous_asteroid', False):
                    processed['potential_hazards'].append({
                        'id': enhanced_neo.get('id'),
                        'name': enhanced_neo.get('name'),
                        'threat_score': enhanced_neo.get('threat_metrics', {}).get('threat_score', 0),
                        'next_approach': enhanced_neo.get('close_approach_data', [{}])[0],
                        'diameter_estimate': self._get_average_diameter(enhanced_neo)
                    })
        
        # Sort hazards by threat score
        processed['potential_hazards'].sort(key=lambda x: x['threat_score'], reverse=True)
        
        return processed

# Global instance
nasa_neo = NASANEOData()